from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.db.models import Q, Sum, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from datetime import date
from products.models import Product
from .utils import Cart
from .models import Notification


class HomeView(TemplateView):
    template_name = "pages/home.html"


class AboutView(TemplateView):
    template_name = "pages/about.html"


class ContactView(TemplateView):
    template_name = "pages/contact.html"


class FAQView(TemplateView):
    template_name = "pages/faq.html"


class ReturnPolicyView(TemplateView):
    template_name = "pages/return_policy.html"


class HowItWorksView(TemplateView):
    template_name = "pages/how_it_works.html"


class ShopView(TemplateView):
    template_name = "pages/shop.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        search_query = self.request.GET.get('search', '')
        category_filter = self.request.GET.get('category', '')
        condition_filter = self.request.GET.get('condition', '')
        min_price = self.request.GET.get('min_price', '')
        max_price = self.request.GET.get('max_price', '')
        sort_by = self.request.GET.get('sort', 'newest')
        
        # Start with all products
        products = Product.objects.filter(certification_status='certified').prefetch_related('images')
        
        # Search filter
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        # Category filter
        if category_filter:
            products = products.filter(category=category_filter)
        
        # Condition filter
        if condition_filter:
            products = products.filter(condition_grade=condition_filter)
        
        # Price filter
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # Sorting
        sort_options = {
            'newest': '-created_at',
            'price_low': 'price',
            'price_high': '-price',
            'name': 'name',
        }
        order_by = sort_options.get(sort_by, '-created_at')
        products = products.order_by(order_by)
        
        # Get unique categories and conditions for filter dropdowns
        all_categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
        all_conditions = Product.CONDITION_CHOICES
        
        # Pagination
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'page_obj': page_obj,
            'products': page_obj.object_list,
            'all_categories': all_categories,
            'all_conditions': all_conditions,
            'search_query': search_query,
            'category_filter': category_filter,
            'condition_filter': condition_filter,
            'min_price': min_price,
            'max_price': max_price,
            'sort_by': sort_by,
        })
        
        return context


class CartView(TemplateView):
    template_name = "pages/cart.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        context['cart_items'] = cart.get_items()
        context['cart_total'] = cart.get_total_price()
        context['cart_count'] = cart.get_total_items()
        return context


@require_POST
def add_to_cart(request):
    """Add product to cart"""
    product_id = request.POST.get('product_id')
    if not product_id:
        messages.error(request, 'Invalid product selection.')
        return redirect('core:shop')

    try:
        product = Product.objects.get(id=product_id, certification_status='certified')
    except Product.DoesNotExist:
        messages.error(request, 'This product is not available.')
        return redirect('core:shop')

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    if quantity < 1:
        quantity = 1

    warranty_plan_id = request.POST.get('warranty_plan')
    if warranty_plan_id == '':
        warranty_plan_id = None

    cart = Cart(request)
    cart.add(product.id, quantity, warranty_plan_id=warranty_plan_id)

    messages.success(request, 'Product added to cart!')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_items(),
            'cart_total': cart.get_total_price()
        })

    return redirect('core:shop')


@require_POST
def remove_from_cart(request):
    """Remove product from cart"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        cart = Cart(request)
        cart.remove(product_id)
        
        messages.success(request, 'Product removed from cart!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': cart.get_total_items(),
                'cart_total': cart.get_total_price()
            })
        
        return redirect('core:cart')
    
    return redirect('core:cart')


@require_POST
def update_cart(request):
    """Update product quantity in cart"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart = Cart(request)
        cart.update(product_id, quantity)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': cart.get_total_items(),
                'cart_total': cart.get_total_price()
            })
        
        return redirect('core:cart')
    
    return redirect('core:cart')



@require_POST
def clear_cart(request):
    """Clear all items from cart"""
    if request.method == 'POST':
        cart = Cart(request)
        cart.clear()
        
        messages.success(request, 'Cart cleared!')
        return redirect('core:shop')
    
    return redirect('core:cart')


# ===== ROLE-BASED DASHBOARD VIEWS =====

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from accounts.decorators import customer_required, seller_required, inspector_required, admin_required


@customer_required
@ensure_csrf_cookie
def customer_dashboard(request):
    """Customer dashboard - view orders and recommendations"""
    from orders.models import Order
    
    orders_qs = Order.objects.filter(user=request.user).prefetch_related('items__product__images', 'status_history')
    recent_orders = list(orders_qs.select_related('address').order_by('-created_at')[:5])

    for order in recent_orders:
        order.primary_item = order.items.first()
        order.latest_status = order.status_history.first()

    active_orders = orders_qs.filter(status__in=[
        'payment_successful', 'confirmed', 'packed', 'shipped', 'out_for_delivery'
    ]).count()
    cancelled_orders = orders_qs.filter(status='cancelled').count()
    total_spent = orders_qs.filter(payment_status__in=['success', 'cod_pending']).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    profile = request.user.customer_profile_safe

    context = {
        'role': 'customer',
        'page_title': 'Customer Dashboard',
        'total_orders': orders_qs.count(),
        'active_orders': active_orders,
        'cancelled_orders': cancelled_orders,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'profile': profile,
        'default_address': getattr(profile, 'default_address', None),
    }
    return render(request, 'dashboards/customer_dashboard.html', context)


@require_GET
def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    results = Product.objects.filter(
        certification_status='certified',
        name__icontains=query
    ).values('id', 'name')[:8]

    return JsonResponse({'results': list(results)})


@seller_required
@ensure_csrf_cookie
def seller_dashboard(request):
    """Seller dashboard - manage submissions and products"""
    from sellers.models import SellerSubmission
    
    seller_submissions = SellerSubmission.objects.filter(seller=request.user)
    
    context = {
        'role': 'seller',
        'page_title': 'Seller Dashboard',
        'total_submissions': seller_submissions.count(),
        'pending_submissions': seller_submissions.filter(status='pending').count(),
        'approved_submissions': seller_submissions.filter(status='approved').count(),
        'rejected_submissions': seller_submissions.filter(status='rejected').count(),
        'recent_submissions': seller_submissions.order_by('-created_at')[:5],
    }
    return render(request, 'dashboards/seller_dashboard.html', context)


@inspector_required
@ensure_csrf_cookie
def inspector_dashboard(request):
    """Inspector dashboard - manage assigned inspections"""
    from inspections.models import Inspection
    
    assigned_inspections = Inspection.objects.filter(inspector=request.user)
    
    context = {
        'role': 'inspector',
        'page_title': 'Inspector Dashboard',
        'total_inspections': assigned_inspections.count(),
        'pending_inspections': assigned_inspections.filter(status='pending').count(),
        'completed_inspections': assigned_inspections.filter(status='completed').count(),
        'recent_inspections': assigned_inspections.order_by('-created_at')[:5],
    }
    return render(request, 'dashboards/inspector_dashboard.html', context)


@admin_required
@ensure_csrf_cookie
def admin_dashboard(request):
    """Admin dashboard - full system overview and management"""
    from django.contrib.auth import get_user_model
    from django.db.models import Sum
    from sellers.models import SellerSubmission
    from inspections.models import Inspection
    from products.models import Product
    from orders.models import Order
    
    User = get_user_model()
    
    # Calculate total revenue
    revenue_data = Order.objects.aggregate(total_revenue=Sum('total_amount'))
    total_revenue = revenue_data['total_revenue'] or 0
    
    context = {
        'role': 'admin',
        'page_title': 'Admin Dashboard',
        'total_users': User.objects.count(),
        'customers': User.objects.filter(role='customer').count(),
        'sellers': User.objects.filter(role='seller').count(),
        'inspectors': User.objects.filter(role='inspector').count(),
        'total_products': Product.objects.count(),
        'certified_products': Product.objects.filter(certification_status='certified').count(),
        'total_orders': Order.objects.count(),
        'total_revenue': total_revenue,
        'total_submissions': SellerSubmission.objects.count(),
        'pending_submissions': SellerSubmission.objects.filter(status='pending').count(),
        'total_inspections': Inspection.objects.count(),
        'pending_inspections': Inspection.objects.filter(status='pending').count(),
        'recent_submissions': SellerSubmission.objects.order_by('-created_at')[:5],
        'recent_inspections': Inspection.objects.order_by('-created_at')[:5],
    }
    return render(request, 'dashboards/admin_dashboard.html', context)


def _parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _get_notification_queryset(request):
    notif_type = request.GET.get('type')
    priority = request.GET.get('priority')
    start_date = _parse_date(request.GET.get('start_date'))
    end_date = _parse_date(request.GET.get('end_date'))

    notifications = Notification.objects.select_related('related_order')

    if notif_type:
        notifications = notifications.filter(type=notif_type)
    if priority:
        notifications = notifications.filter(priority=priority)
    if start_date:
        notifications = notifications.filter(created_at__date__gte=start_date)
    if end_date:
        notifications = notifications.filter(created_at__date__lte=end_date)

    return notifications


def _get_summary_cards():
    from orders.models import Order

    today = timezone.localdate()
    new_orders_today = Order.objects.filter(created_at__date=today).count()
    pending_refunds = Order.objects.filter(refund_id__isnull=False).exclude(
        refund_status__in=['processed', 'success', 'completed']
    ).count()
    failed_payments = Order.objects.filter(payment_status='failed').count()
    unread_notifications = Notification.objects.filter(is_read=False).count()
    low_stock_alerts = Product.objects.filter(stock_quantity__lte=F('low_stock_threshold')).count()

    return {
        'new_orders_today': new_orders_today,
        'pending_refunds': pending_refunds,
        'failed_payments': failed_payments,
        'unread_notifications': unread_notifications,
        'low_stock_alerts': low_stock_alerts,
    }


@admin_required
@ensure_csrf_cookie
def admin_notification_dashboard(request):
    notifications = _get_notification_queryset(request)
    paginator = Paginator(notifications, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'role': 'admin',
        'page_title': 'Admin Notifications',
        'notifications': page_obj.object_list,
        'page_obj': page_obj,
        'filters': {
            'type': request.GET.get('type', ''),
            'priority': request.GET.get('priority', ''),
            'start_date': request.GET.get('start_date', ''),
            'end_date': request.GET.get('end_date', ''),
        },
        'summary': _get_summary_cards(),
        'type_choices': Notification.TYPE_CHOICES,
        'priority_choices': Notification.PRIORITY_CHOICES,
    }
    return render(request, 'dashboards/admin_notification_dashboard.html', context)


@admin_required
@require_GET
def admin_notification_data(request):
    notifications = _get_notification_queryset(request)
    paginator = Paginator(notifications, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    data = []
    for item in page_obj.object_list:
        related_order = item.related_order
        data.append({
            'id': item.id,
            'title': item.title,
            'message': item.message,
            'type': item.type,
            'priority': item.priority,
            'is_read': item.is_read,
            'created_at': item.created_at.isoformat(),
            'created_at_display': timezone.localtime(item.created_at).strftime('%Y-%m-%d %H:%M'),
            'related_order_id': related_order.id if related_order else None,
            'related_order_number': related_order.order_number if related_order else None,
        })

    return JsonResponse({
        'notifications': data,
        'summary': _get_summary_cards(),
        'pagination': {
            'page': page_obj.number,
            'pages': page_obj.paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })


@admin_required
@require_POST
def admin_notification_mark_read(request):
    notification_id = request.POST.get('notification_id')
    if not notification_id:
        return JsonResponse({'success': False, 'error': 'Missing notification_id'}, status=400)

    updated = Notification.objects.filter(id=notification_id, is_read=False).update(is_read=True)
    return JsonResponse({'success': True, 'updated': updated})
