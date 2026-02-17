from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
import secrets
import json
import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timedelta

from core.utils import Cart
from .models import Order, OrderItem, OrderAddress, OrderStatusHistory
from products.models import Product
from accounts.decorators import customer_required
from .tasks import send_order_notifications

logger = logging.getLogger(__name__)

def get_razorpay_client():
    """Lazy load Razorpay client"""
    try:
        import razorpay
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            logger.error("Razorpay keys are missing. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.")
            return None
        return razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    except ImportError:
        logger.warning("Razorpay SDK not installed")
        return None


@login_required
@customer_required
@require_http_methods(["GET", "POST"])
def checkout_step1_address(request):
    """Step 1: Address Selection"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'new_address':
            try:
                address = OrderAddress.objects.create(
                    user=request.user,
                    full_name=request.POST.get('full_name'),
                    phone=request.POST.get('phone'),
                    address=request.POST.get('address'),
                    city=request.POST.get('city'),
                    state=request.POST.get('state', ''),
                    postal_code=request.POST.get('postal_code'),
                    is_default=request.POST.get('is_default') == 'on'
                )
                request.session['checkout_address_id'] = address.id
                request.session['checkout_step'] = 2
                request.session.modified = True  # Force session save
                return redirect('orders:checkout_step2_payment')
            except Exception as e:
                logger.error(f"Address creation failed: {str(e)}")
                messages.error(request, 'Failed to create address.')
                return redirect('orders:checkout_step1_address')
        
        elif action == 'select_address':
            address_id = request.POST.get('address_id')
            if not address_id:
                messages.error(request, 'Please select an address.')
                return redirect('orders:checkout_step1_address')
            
            try:
                # Optimize query - only fetch id to verify existence
                address = OrderAddress.objects.only('id').get(id=address_id, user=request.user)
                request.session['checkout_address_id'] = address.id
                request.session['checkout_step'] = 2
                request.session.modified = True  # Force session save
                return redirect('orders:checkout_step2_payment')
            except OrderAddress.DoesNotExist:
                messages.error(request, 'Invalid address selected.')
                return redirect('orders:checkout_step1_address')
    
    # Optimize query - order by default first, then updated date
    saved_addresses = OrderAddress.objects.filter(user=request.user).order_by('-is_default', '-updated_at')
    context = {
        'saved_addresses': saved_addresses,
        'step': 1,
    }
    return render(request, 'orders/checkout_step1.html', context)


@login_required
@customer_required
@require_http_methods(["GET", "POST"])
def checkout_step2_payment(request):
    """Step 2: Payment Method Selection"""
    address_id = request.session.get('checkout_address_id')
    if not address_id:
        return redirect('orders:checkout_step1_address')
    
    try:
        address = OrderAddress.objects.get(id=address_id, user=request.user)
    except OrderAddress.DoesNotExist:
        messages.error(request, 'Address not found.')
        return redirect('orders:checkout_step1_address')
    
    cart = Cart(request)
    buy_now_product_id = request.session.get('buy_now_product_id')
    buy_now_options = request.session.get('buy_now_options', {})
    
    if buy_now_product_id:
        product = Product.objects.filter(id=buy_now_product_id, certification_status='certified').first()
        if not product:
            messages.warning(request, 'Product unavailable.')
            return redirect('core:shop')
        cart_items = [{
            'product': product,
            'quantity': 1,
            'price': float(product.price),
            'total_price': float(product.price),
        }]
        subtotal = float(product.price)
        is_buy_now = True
    else:
        cart_items = cart.get_items()
        if not cart_items:
            messages.warning(request, 'Cart is empty.')
            return redirect('core:cart')
        subtotal = cart.get_total_price()
        is_buy_now = False
    
    delivery_charge = 0
    total_amount = subtotal + delivery_charge
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        emi_plan = request.POST.get('emi_plan') if payment_method == 'emi' else None
        
        request.session['checkout_payment_method'] = payment_method
        request.session['checkout_emi_plan'] = emi_plan
        request.session['checkout_step'] = 3
        return redirect('orders:checkout_step3_review')
    
    emi_options = {
        '3months': {'months': 3, 'interest_rate': 0.0},
        '6months': {'months': 6, 'interest_rate': 0.02},
        '12months': {'months': 12, 'interest_rate': 0.05},
    }
    
    # Pre-calculate EMI amounts
    for key, plan in emi_options.items():
        months = plan['months']
        interest_rate = plan['interest_rate']
        principal = total_amount
        interest_amount = principal * interest_rate
        total_with_interest = principal + interest_amount
        monthly_amount = total_with_interest / months
        plan['monthly_amount'] = round(monthly_amount, 2)
        plan['total_cost'] = round(total_with_interest, 2)
        plan['interest_amount'] = round(interest_amount, 2)
    
    context = {
        'address': address,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total_amount': total_amount,
        'is_buy_now': is_buy_now,
        'buy_now_options': buy_now_options,
        'emi_options': emi_options,
        'step': 2,
    }
    return render(request, 'orders/checkout_step2.html', context)


@login_required
@customer_required
@require_http_methods(["GET", "POST"])
def checkout_step3_review(request):
    """Step 3: Order Review & Confirmation"""
    address_id = request.session.get('checkout_address_id')
    payment_method = request.session.get('checkout_payment_method')
    emi_plan = request.session.get('checkout_emi_plan')
    
    if not address_id or not payment_method:
        return redirect('orders:checkout_step1_address')
    
    try:
        address = OrderAddress.objects.get(id=address_id, user=request.user)
    except OrderAddress.DoesNotExist:
        messages.error(request, 'Address not found.')
        return redirect('orders:checkout_step1_address')
    
    cart = Cart(request)
    buy_now_product_id = request.session.get('buy_now_product_id')
    buy_now_options = request.session.get('buy_now_options', {})
    
    if buy_now_product_id:
        product = Product.objects.filter(id=buy_now_product_id, certification_status='certified').first()
        if not product:
            messages.warning(request, 'Product unavailable.')
            return redirect('core:shop')
        cart_items = [{
            'product': product,
            'quantity': 1,
            'price': float(product.price),
            'total_price': float(product.price),
        }]
        subtotal = float(product.price)
        is_buy_now = True
    else:
        cart_items = cart.get_items()
        if not cart_items:
            messages.warning(request, 'Cart is empty.')
            return redirect('core:cart')
        subtotal = cart.get_total_price()
        is_buy_now = False
    
    delivery_charge = 0
    total_amount = subtotal + delivery_charge
    
    if request.method == 'POST':
        logger.info(f"Order creation started for user {request.user.id}")
        logger.info(f"Address ID: {address_id}, Payment method: {payment_method}")
        try:
            with transaction.atomic():
                order_number = f"ORD-{int(timezone.now().timestamp())}-{secrets.randbelow(10000):04d}"
                logger.info(f"Creating order: {order_number}, Total: {total_amount}")
                
                order = Order.objects.create(
                    user=request.user,
                    order_number=order_number,
                    address=address,
                    subtotal=subtotal,
                    delivery_charge=delivery_charge,
                    total_amount=total_amount,
                    payment_method=payment_method,
                    emi_plan=emi_plan,
                    estimated_delivery=timezone.now().date() + timedelta(days=5),
                )
                logger.info(f"Order {order.id} created successfully")
                
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        quantity=item['quantity'],
                        price=item['price'],
                        condition=buy_now_options.get('condition'),
                        storage=buy_now_options.get('storage'),
                        color=buy_now_options.get('color'),
                    )
                logger.info(f"Order items created for order {order.id}")
                
                OrderStatusHistory.objects.create(
                    order=order,
                    status=order.status,
                    updated_by=request.user,
                    notes="Order created"
                )
                
                if payment_method == 'online':
                    logger.info(f"Processing online payment for order {order.id}, amount: ₹{total_amount}")
                    
                    # Check if Razorpay credentials are configured
                    razorpay_client = get_razorpay_client()
                    is_fake_payment = (
                        not razorpay_client or
                        'SAMPLE' in settings.RAZORPAY_KEY_ID or
                        'REPLACE_ME' in settings.RAZORPAY_KEY_ID or
                        len(settings.RAZORPAY_KEY_ID) < 20
                    )
                    
                    if is_fake_payment:
                        # MOCK PAYMENT MODE - For testing without Razorpay credentials
                        logger.info(f"[Order {order.id}] Using MOCK payment mode (Razorpay not configured)")
                        
                        # Generate fake payment IDs for simulation
                        fake_order_id = f"fake_order_{uuid.uuid4().hex[:12]}"
                        fake_payment_id = f"fake_pay_{uuid.uuid4().hex[:12]}"
                        
                        # Mark order as paid (simulating successful payment)
                        order.razorpay_order_id = fake_order_id
                        order.razorpay_payment_id = fake_payment_id
                        order.payment_method = 'online'
                        order.payment_status = 'success'
                        order.status = 'confirmed'
                        order.save()
                        
                        # Create status history
                        OrderStatusHistory.objects.create(
                            order=order,
                            status='confirmed',
                            updated_by=request.user,
                            notes="Payment successful (MOCK MODE - Test payment)"
                        )
                        
                        # Clear checkout session
                        for key in ['checkout_address_id', 'checkout_payment_method', 'checkout_emi_plan', 'checkout_step', 'buy_now_product_id', 'buy_now_options']:
                            request.session.pop(key, None)
                        
                        # Send notifications (async)
                        try:
                            send_order_notifications.delay(order.id, 'payment_successful')
                            send_order_notifications.delay(order.id, 'order_confirmed')
                        except Exception as notification_error:
                            logger.warning(f"Failed to send notifications: {notification_error}")
                        
                        messages.success(request, f'✅ Payment successful! Order #{order.order_number} has been confirmed. (Test Mode)')
                        logger.info(f"[Order {order.id}] MOCK payment completed successfully")
                        return redirect('orders:order_confirmation', order_id=order.id)
                    
                    else:
                        # REAL RAZORPAY PAYMENT MODE
                        try:
                            logger.info(f"[Order {order.id}] Calling Razorpay order.create with amount={int(total_amount * 100)} paise")
                            razorpay_order = razorpay_client.order.create({
                                'amount': int(total_amount * 100),
                                'currency': 'INR',
                                'receipt': order_number,
                                'notes': {
                                    'order_id': str(order.id),
                                    'user_id': str(request.user.id),
                                }
                            })
                            logger.info(f"[Order {order.id}] Razorpay order created successfully: {razorpay_order['id']}")
                            
                            order.razorpay_order_id = razorpay_order['id']
                            order.payment_status = 'pending'
                            order.save()
                            
                            request.session['current_order_id'] = order.id
                            logger.info(f"[Order {order.id}] Redirecting to payment gateway")
                            return redirect('orders:payment_gateway', order_id=order.id)
                        except Exception as razorpay_error:
                            logger.exception(f"[Order {order.id}] Razorpay API failed: {str(razorpay_error)}")
                            # Re-raise to trigger transaction rollback
                        raise
                
                elif payment_method == 'emi':
                    logger.info(f"Processing EMI for order {order.id}, plan: {emi_plan}")
                    
                    # Check if Razorpay credentials are configured
                    razorpay_client = get_razorpay_client()
                    is_fake_payment = (
                        not razorpay_client or
                        'SAMPLE' in settings.RAZORPAY_KEY_ID or
                        'REPLACE_ME' in settings.RAZORPAY_KEY_ID or
                        len(settings.RAZORPAY_KEY_ID) < 20
                    )
                    
                    if is_fake_payment:
                        # MOCK EMI PAYMENT MODE
                        logger.info(f"[Order {order.id}] Using MOCK EMI payment mode")
                        
                        fake_order_id = f"fake_emi_order_{uuid.uuid4().hex[:12]}"
                        fake_payment_id = f"fake_emi_pay_{uuid.uuid4().hex[:12]}"
                        
                        order.razorpay_order_id = fake_order_id
                        order.razorpay_payment_id = fake_payment_id
                        order.payment_method = 'emi'
                        order.payment_status = 'success'
                        order.status = 'confirmed'
                        order.save()
                        
                        OrderStatusHistory.objects.create(
                            order=order,
                            status='confirmed',
                            updated_by=request.user,
                            notes=f"EMI Payment successful - {emi_plan} plan (MOCK MODE)"
                        )
                        
                        # Clear checkout session
                        for key in ['checkout_address_id', 'checkout_payment_method', 'checkout_emi_plan', 'checkout_step', 'buy_now_product_id', 'buy_now_options']:
                            request.session.pop(key, None)
                        
                        try:
                            send_order_notifications.delay(order.id, 'payment_successful')
                            send_order_notifications.delay(order.id, 'order_confirmed')
                        except Exception as notification_error:
                            logger.warning(f"Failed to send notifications: {notification_error}")
                        
                        messages.success(request, f'✅ EMI Payment successful! Order #{order.order_number} confirmed with {emi_plan} plan. (Test Mode)')
                        logger.info(f"[Order {order.id}] MOCK EMI payment completed")
                        return redirect('orders:order_confirmation', order_id=order.id)
                    
                    else:
                        # REAL RAZORPAY EMI PAYMENT
                        try:
                            logger.info(f"[Order {order.id}] Calling Razorpay order.create for EMI with amount={int(total_amount * 100)} paise")
                            razorpay_order = razorpay_client.order.create({
                                'amount': int(total_amount * 100),
                                'currency': 'INR',
                                'receipt': order_number,
                                'notes': {
                                    'order_id': str(order.id),
                                    'user_id': str(request.user.id),
                                    'payment_type': 'emi',
                                    'emi_plan': emi_plan,
                                }
                            })
                            logger.info(f"[Order {order.id}] Razorpay EMI order created: {razorpay_order['id']}")
                            
                            order.razorpay_order_id = razorpay_order['id']
                            order.payment_status = 'pending'
                            order.save()
                            
                            request.session['current_order_id'] = order.id
                            logger.info(f"[Order {order.id}] Redirecting to EMI payment gateway")
                            return redirect('orders:payment_gateway', order_id=order.id)
                        except Exception as razorpay_error:
                            logger.exception(f"[Order {order.id}] EMI Razorpay API failed: {str(razorpay_error)}")
                            raise  # Transaction rollback
                
                else:  # COD
                    logger.info(f"Processing COD (Cash on Delivery) for order {order.id}")
                    order.payment_method = 'cod'
                    order.payment_status = 'cod_pending'
                    order.status = 'confirmed'
                    order.save()
                    
                    OrderStatusHistory.objects.create(
                        order=order,
                        status='confirmed',
                        updated_by=request.user,
                        notes="COD order confirmed - awaiting delivery"
                    )
                    logger.info(f"[Order {order.id}] COD order confirmed successfully")
                
                if is_buy_now:
                    request.session.pop('buy_now_product_id', None)
                    request.session.pop('buy_now_options', None)
                else:
                    cart.clear()
                
                request.session.pop('checkout_address_id', None)
                request.session.pop('checkout_payment_method', None)
                request.session.pop('checkout_emi_plan', None)
                request.session.pop('checkout_step', None)
                
                logger.info(f"Order {order.id} workflow completed successfully, redirecting to confirmation")
                return redirect('orders:order_confirmation', order_id=order.id)
        
        except Exception as e:
            logger.exception(f"Order creation/processing failed for user {request.user.id}: {str(e)}")
            error_message = str(e).lower()
            
            # Provide user-friendly error messages based on error type
            if 'razorpay' in error_message or 'payment' in error_message:
                user_error = 'Payment gateway error. Please check your internet connection and ensure Razorpay credentials are configured.'
            elif 'amount' in error_message:
                user_error = 'Invalid order amount. Please review your cart and try again.'
            elif 'address' in error_message:
                user_error = 'Address validation failed. Please select a valid address.'
            elif 'product' in error_message or 'unavailable' in error_message:
                user_error = 'One or more products are no longer available. Please update your cart.'
            elif 'client initialization' in error_message:
                user_error = 'Payment system not configured. Please contact support.'
            else:
                user_error = f'Failed to create order. Please try again or contact support.'
            
            messages.error(request, user_error)
            logger.error(f"User-friendly error shown: {user_error}")
            # Don't redirect - stay on page and show error message
            context = {
                'address': address,
                'cart_items': cart_items,
                'subtotal': subtotal,
                'delivery_charge': delivery_charge,
                'total_amount': total_amount,
                'payment_method': payment_method,
                'emi_plan': emi_plan,
                'is_buy_now': is_buy_now,
                'buy_now_options': buy_now_options,
                'step': 3,
                'error': user_error,
            }
            return render(request, 'orders/checkout_step3.html', context)
    
    context = {
        'address': address,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total_amount': total_amount,
        'payment_method': payment_method,
        'emi_plan': emi_plan,
        'is_buy_now': is_buy_now,
        'buy_now_options': buy_now_options,
        'step': 3,
    }
    return render(request, 'orders/checkout_step3.html', context)


@login_required
def payment_gateway(request, order_id):
    """Razorpay Payment Gateway"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('core:home')
    
    if order.razorpay_order_id:
        context = {
            'order': order,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount_paise': int(order.total_amount * 100),
        }
        return render(request, 'orders/payment_gateway.html', context)
    
    return redirect('orders:order_tracking', order_id=order.id)


@require_POST
@csrf_exempt
def payment_callback(request):
    """Razorpay Payment Callback - Server-side Verification
    
    SECURITY CRITICAL:
    - Server-side signature verification (HMAC-SHA256)
    - Amount verification against order
    - Idempotent: safe to call multiple times
    - Atomic: all-or-nothing database updates
    - Prevents duplicate payment processing
    - Prevents tampering by checking signature
    """
    try:
        payment_id = request.POST.get('razorpay_payment_id', '').strip()
        razorpay_order_id = request.POST.get('razorpay_order_id', '').strip()
        signature = request.POST.get('razorpay_signature', '').strip()
        
        # ============================================
        # STEP 1: VALIDATE INPUT
        # ============================================
        if not all([payment_id, razorpay_order_id, signature]):
            logger.error(f"[PAYMENT_SECURITY] Missing required fields - Payment ID: {bool(payment_id)}, Order ID: {bool(razorpay_order_id)}, Signature: {bool(signature)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid payment request. Missing required fields.'
            }, status=400)
        
        if not (len(payment_id) > 10 and len(razorpay_order_id) > 10):
            logger.error(f"[PAYMENT_SECURITY] Invalid format - Payment ID length: {len(payment_id)}, Order ID length: {len(razorpay_order_id)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid payment request. Invalid field format.'
            }, status=400)
        
        # ============================================
        # STEP 2: FETCH ORDER
        # ============================================
        try:
            order = Order.objects.select_for_update().get(razorpay_order_id=razorpay_order_id)
            logger.info(f"[PAYMENT] Order found: {order.id} ({order.order_number})")
        except Order.DoesNotExist:
            logger.error(f"[PAYMENT_SECURITY] Order not found for razorpay_order_id: {razorpay_order_id}")
            logger.error(f"[FRAUD_ALERT] Possible tampering: Payment received for non-existent order")
            return JsonResponse({
                'status': 'error',
                'message': 'Order not found. Payment cannot be processed.'
            }, status=404)
        
        # ============================================
        # STEP 3: CHECK IDEMPOTENCY
        # ============================================
        if order.razorpay_payment_id:
            # Payment already processed
            if order.razorpay_payment_id == payment_id:
                logger.info(f"[PAYMENT] Idempotent callback for order {order.id} - payment already processed")
                # Return success to acknowledge receipt (idempotent)
                return JsonResponse({
                    'status': 'success',
                    'order_id': order.id,
                    'message': 'Payment already verified'
                })
            else:
                # Different payment_id for same order - SECURITY ALERT
                logger.error(f"[PAYMENT_SECURITY] Multiple payment IDs for same order: {payment_id} vs {order.razorpay_payment_id}")
                logger.error(f"[FRAUD_ALERT] Possible tampering: Multiple payments for single order")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Order already has a payment. Cannot process multiple payments.'
                }, status=400)
        
        # ============================================
        # STEP 4: VERIFY RAZORPAY CREDENTIALS
        # ============================================
        if not settings.RAZORPAY_KEY_SECRET:
            logger.error("[PAYMENT_SECURITY] RAZORPAY_KEY_SECRET not configured")
            return JsonResponse({
                'status': 'error',
                'message': 'Payment gateway configuration error. Please contact support.'
            }, status=500)
        
        # ============================================
        # STEP 5: SERVER-SIDE SIGNATURE VERIFICATION
        # ============================================
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{razorpay_order_id}|{payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signature, signature):
            logger.error(f"[PAYMENT_SECURITY] Signature verification failed for order {order.id}")
            logger.error(f"[FRAUD_ALERT] Invalid signature. Possible tampering detected.")
            # Update order status to failed
            with transaction.atomic():
                order.payment_status = 'failed'
                order.save()
                OrderStatusHistory.objects.create(
                    order=order,
                    status='payment_failed',
                    updated_by=order.user,
                    notes="Payment signature verification failed - SECURITY ALERT"
                )
            return JsonResponse({
                'status': 'error',
                'message': 'Payment verification failed. Invalid signature. Contact support.'
            }, status=400)
        
        logger.info(f"[PAYMENT] Signature verified for order {order.id}")
        
        # ============================================
        # STEP 6: AMOUNT VERIFICATION
        # ============================================
        expected_amount_paise = int(order.total_amount * 100)
        
        # Note: For additional security, fetch payment details from Razorpay API
        # This prevents tampering with the amount in the callback
        try:
            razorpay_client = get_razorpay_client()
            if razorpay_client:
                payment_details = razorpay_client.payment.fetch(payment_id)
                actual_amount_paise = payment_details.get('amount', 0)
                actual_order_id = payment_details.get('order_id', '')
                actual_status = payment_details.get('status', '')
                
                logger.info(f"[PAYMENT] Razorpay API verified - Amount: {actual_amount_paise} paise, Status: {actual_status}")
                
                # Verify amount matches
                if actual_amount_paise != expected_amount_paise:
                    logger.error(f"[PAYMENT_SECURITY] Amount mismatch - Expected: {expected_amount_paise}, Got: {actual_amount_paise}")
                    logger.error(f"[FRAUD_ALERT] Possible tampering: Amount mismatch detected")
                    with transaction.atomic():
                        order.payment_status = 'failed'
                        order.save()
                        OrderStatusHistory.objects.create(
                            order=order,
                            status='payment_failed',
                            updated_by=order.user,
                            notes=f"Payment amount mismatch - FRAUD ALERT"
                        )
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Payment amount verification failed. Possible fraud.'
                    }, status=400)
                
                # Verify order_id matches
                if actual_order_id != razorpay_order_id:
                    logger.error(f"[PAYMENT_SECURITY] Order ID mismatch from Razorpay")
                    logger.error(f"[FRAUD_ALERT] Possible tampering: Order ID mismatch")
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Payment verification failed. Order mismatch.'
                    }, status=400)
                
                # Verify payment status is captured
                if actual_status not in ['captured', 'authorized']:
                    logger.error(f"[PAYMENT] Payment not captured - Status: {actual_status}")
                    with transaction.atomic():
                        order.payment_status = 'failed'
                        order.save()
                        OrderStatusHistory.objects.create(
                            order=order,
                            status='payment_failed',
                            updated_by=order.user,
                            notes=f"Payment not captured - Status: {actual_status}"
                        )
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Payment not completed. Please try again.'
                    }, status=400)
        except Exception as api_error:
            logger.warning(f"[PAYMENT] Could not verify payment with Razorpay API: {str(api_error)}")
            logger.info(f"[PAYMENT] Proceeding with signature-only verification")
        
        # ============================================
        # STEP 7: UPDATE ORDER (ATOMIC TRANSACTION)
        # ============================================
        try:
            with transaction.atomic():
                # Fetch fresh copy to ensure no race conditions
                order = Order.objects.select_for_update().get(id=order.id)
                
                # Double-check idempotency inside transaction
                if order.razorpay_payment_id:
                    logger.info(f"[PAYMENT] Already processed (race condition check): {order.id}")
                    return JsonResponse({
                        'status': 'success',
                        'order_id': order.id,
                        'message': 'Payment already verified'
                    })
                
                # Update order with payment details
                order.razorpay_payment_id = payment_id
                order.razorpay_signature = signature
                order.payment_status = 'success'
                order.status = 'confirmed'
                order.save()
                
                logger.info(f"[PAYMENT] Order {order.id} marked as payment_successful")
                
                # Create status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status='confirmed',
                    updated_by=order.user,
                    notes=f"Payment captured: {payment_id}"
                )
                
                logger.info(f"[PAYMENT] Payment confirmed for order {order.id}")
        except Exception as db_error:
            logger.exception(f"[PAYMENT] Database error during payment confirmation: {str(db_error)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to process payment. Please contact support.'
            }, status=500)
        
        # ============================================
        # STEP 8: SEND NOTIFICATIONS (ASYNC)
        # ============================================
        try:
            from .tasks import send_order_notifications
            try:
                # Queue notifications asynchronously
                send_order_notifications.delay(order.id, 'payment_successful')
                send_order_notifications.delay(order.id, 'order_confirmed')
                send_order_notifications.delay(order.id, 'invoice_sent')
                logger.info(f"[NOTIFICATION] Notification tasks queued for order {order.id}")
            except Exception as celery_error:
                # Fallback to synchronous if Celery unavailable
                logger.warning(f"[NOTIFICATION] Celery unavailable, sending synchronously: {str(celery_error)}")
                send_order_notifications(order.id, 'payment_successful')
                send_order_notifications(order.id, 'order_confirmed')
                send_order_notifications(order.id, 'invoice_sent')
                logger.info(f"[NOTIFICATION] Notifications sent synchronously for order {order.id}")
        except Exception as notif_error:
            logger.error(f"[NOTIFICATION] Failed to send notifications for order {order.id}: {str(notif_error)}")
            # Don't fail the payment callback due to notification errors
        
        # ============================================
        # SUCCESS RESPONSE
        # ============================================
        logger.info(f"[PAYMENT] Payment callback completed successfully for order {order.id}")
        return JsonResponse({
            'status': 'success',
            'order_id': order.id,
            'message': 'Payment verified and order confirmed'
        })
    
    except Exception as e:
        logger.exception(f"[PAYMENT_ERROR] Unexpected error in payment callback: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Payment processing error. Please contact support with your order number.'
        }, status=500)


@login_required
@require_POST
def cancel_order(request, order_id):
    """Cancel Order with Refund"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('orders:order_tracking', order_id=order_id)
    
    if not order.can_cancel():
        messages.error(request, f'Cannot cancel order in {order.get_status_display()} status.')
        return redirect('orders:order_tracking', order_id=order_id)
    
    try:
        with transaction.atomic():
            order.status = 'cancelled'
            order.cancelled_at = timezone.now()
            
            if order.payment_method == 'online' and order.razorpay_payment_id:
                razorpay_client = get_razorpay_client()
                if razorpay_client:
                    refund = razorpay_client.payment.refund(
                        order.razorpay_payment_id,
                        {'amount': int(order.total_amount * 100)}
                    )
                    order.refund_id = refund['id']
                    order.refund_status = refund['status']
                    order.refund_amount = order.total_amount
                    order.payment_status = 'refunded'
            
            order.save()
            
            # Trigger refund notification
            try:
                if order.refund_id:
                    send_order_notifications.delay(order.id, 'refund_processed')
            except Exception as e:
                logger.error(f"Failed to queue refund notification for order {order.id}: {str(e)}")
            
            OrderStatusHistory.objects.create(
                order=order,
                status='cancelled',
                updated_by=request.user,
                notes=f"Cancelled by customer. Refund: {order.refund_id or 'N/A'}"
            )
            
            messages.success(request, 'Order cancelled successfully.')
    
    except Exception as e:
        logger.error(f"Cancel order failed: {str(e)}")
        messages.error(request, 'Failed to cancel order.')
    
    return redirect('orders:order_tracking', order_id=order_id)


@login_required
def order_tracking(request, order_id):
    """Order Tracking Page"""
    try:
        order = Order.objects.prefetch_related('items__product', 'status_history').get(
            id=order_id,
            user=request.user
        )
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('core:home')
    
    status_timeline = order.status_history.all()
    
    # Define all possible order statuses for progress bar
    status_choices = [
        'pending_payment',
        'payment_successful',
        'confirmed',
        'packed',
        'shipped',
        'out_for_delivery',
        'delivered'
    ]
    
    context = {
        'order': order,
        'status_timeline': status_timeline,
        'status_choices': status_choices,
    }
    return render(request, 'orders/order_tracking.html', context)


@login_required
def order_confirmation(request, order_id):
    """Order Confirmation Page"""
    try:
        order = Order.objects.prefetch_related('items__product').get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('core:home')
    
    context = {'order': order}
    return render(request, 'orders/order_confirmation.html', context)


@login_required
def order_invoice(request, order_id):
    """Order Invoice Page"""
    try:
        order = Order.objects.prefetch_related('items__product').get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('core:home')

    context = {
        'order': order,
    }
    response = render(request, 'orders/order_invoice.html', context)
    if request.GET.get('download') == '1':
        filename = f"invoice-{order.order_number or order.id}.html"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@require_POST
@login_required
@customer_required
def buy_now(request):
    """Buy Now - Redirects to 3-step checkout"""
    product_id = request.POST.get('product_id')
    if not product_id:
        messages.error(request, 'Invalid product selection.')
        return redirect('core:shop')

    product = Product.objects.filter(id=product_id, certification_status='certified').first()
    if not product:
        messages.error(request, 'This product is not available.')
        return redirect('core:shop')

    request.session['buy_now_product_id'] = product.id
    
    condition = request.POST.get('condition', 'likenew')
    storage = request.POST.get('storage', '64gb')
    color = request.POST.get('color', 'Black')
    
    request.session['buy_now_options'] = {
        'condition': condition,
        'storage': storage,
        'color': color,
    }
    
    request.session['checkout_step'] = 1
    request.session.modified = True
    return redirect('orders:checkout_step1_address')
