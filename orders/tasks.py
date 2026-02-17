from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging
import requests
import json

from .models import Order, NotificationLog

logger = logging.getLogger(__name__)
User = get_user_model()


# =============================================================================
# SYNCHRONOUS HELPER FUNCTIONS (can be called directly without Celery)
# =============================================================================

def _send_email_sync(order_id, event_type):
    """Synchronous email sending - works without Celery/Redis"""
    try:
        order = Order.objects.select_related('user', 'address').prefetch_related('items__product').get(id=order_id)
        
        email_templates = {
            'order_confirmed': {
                'subject': f'Order Confirmed - {order.order_number}',
                'template': 'emails/order_confirmed.html'
            },
            'payment_successful': {
                'subject': f'Payment Successful - {order.order_number}',
                'template': 'emails/payment_successful.html'
            },
            'invoice_sent': {
                'subject': f'Invoice Ready - {order.order_number}',
                'template': 'emails/invoice_sent.html'
            },
            'order_shipped': {
                'subject': f'Order Shipped - {order.order_number}',
                'template': 'emails/order_shipped.html'
            },
            'out_for_delivery': {
                'subject': f'Out for Delivery - {order.order_number}',
                'template': 'emails/out_for_delivery.html'
            },
            'order_delivered': {
                'subject': f'Order Delivered - {order.order_number}',
                'template': 'emails/order_delivered.html'
            },
            'refund_processed': {
                'subject': f'Refund Processed - {order.order_number}',
                'template': 'emails/refund_processed.html'
            },
        }
        
        email_config = email_templates.get(event_type)
        if not email_config:
            logger.error(f"Unknown event type: {event_type}")
            return
        
        notification_log = NotificationLog.objects.create(
            user=order.user,
            order=order,
            notification_type='email',
            event_type=event_type,
            recipient=order.user.email,
            status='pending'
        )
        
        try:
            context = {
                'user': order.user,
                'order': order,
                'items': order.items.all(),
                'site_name': 'CERTIBUY',
                'support_email': settings.DEFAULT_FROM_EMAIL,
            }
            
            html_content = render_to_string(email_config['template'], context)
            text_content = f"Order {order.order_number} - {email_config['subject']}"
            
            email = EmailMultiAlternatives(
                subject=email_config['subject'],
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[order.user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            notification_log.status = 'sent'
            notification_log.sent_at = timezone.now()
            notification_log.response_log = 'Email sent successfully'
            notification_log.save()
            
            logger.info(f"✓ Email sent: {event_type} for order {order.order_number}")
            
        except Exception as e:
            notification_log.status = 'failed'
            notification_log.error_message = str(e)
            notification_log.retry_count += 1
            notification_log.save()
            
            logger.error(f"✗ Email failed: {event_type} for order {order.order_number} - {str(e)}")
            raise
    
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found for email notification")
    except Exception as e:
        logger.exception(f"Email error: {str(e)}")
        raise


def _send_sms_sync(order_id, event_type):
    """Synchronous SMS sending - works without Celery/Redis"""
    try:
        order = Order.objects.select_related('user', 'address').get(id=order_id)
        
        if not order.address or not order.address.phone:
            logger.warning(f"No phone number for order {order.order_number}")
            return
        
        sms_templates = {
            'payment_successful': f'Payment successful for order {order.order_number}. Amount: Rs.{order.total_amount}. - CERTIBUY',
            'order_confirmed': f'Order {order.order_number} confirmed. Track at certibuy.com. - CERTIBUY',
            'invoice_sent': f'Invoice for order {order.order_number} (Rs.{order.total_amount}). Download at certibuy.com/orders/{order.id}/invoice/. - CERTIBUY',
            'order_shipped': f'Your order {order.order_number} has been shipped. Tracking: {order.tracking_id or "Pending"}. - CERTIBUY',
            'out_for_delivery': f'Order {order.order_number} is out for delivery. Expect delivery today. - CERTIBUY',
            'order_delivered': f'Order {order.order_number} has been delivered. Thank you! - CERTIBUY',
            'refund_issued': f'Refund of Rs.{order.refund_amount} processed for order {order.order_number}. - CERTIBUY',
        }
        
        message = sms_templates.get(event_type)
        if not message:
            logger.error(f"Unknown SMS event type: {event_type}")
            return
        
        notification_log = NotificationLog.objects.create(
            user=order.user,
            order=order,
            notification_type='sms',
            event_type=event_type,
            recipient=order.address.phone,
            status='pending'
        )
        
        try:
            from orders.services.sms_service import send_sms
            
            response = send_sms(
                phone=order.address.phone,
                message=message,
                order_id=order.order_number
            )
            
            if response.get('status') == 'success':
                notification_log.status = 'sent'
                notification_log.sent_at = timezone.now()
                notification_log.response_log = json.dumps(response)
                logger.info(f"✓ SMS sent: {event_type} for order {order.order_number} to {order.address.phone}")
            else:
                notification_log.status = 'failed'
                notification_log.error_message = response.get('message', 'Unknown error')
                notification_log.response_log = json.dumps(response)
                logger.error(f"✗ SMS failed: {event_type} for order {order.order_number}")
            
            notification_log.retry_count += 1
            notification_log.save()
            
        except Exception as e:
            notification_log.status = 'failed'
            notification_log.error_message = str(e)
            notification_log.retry_count += 1
            notification_log.save()
            
            logger.error(f"SMS error: {event_type} for order {order.order_number} - {str(e)}")
            raise
    
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found for SMS notification")
    except Exception as e:
        logger.exception(f"SMS error: {str(e)}")
        raise


# =============================================================================
# CELERY TASKS (async, requires Redis + Celery worker)
# =============================================================================

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_email(self, order_id, event_type):
    """Send order-related email notification (Celery task)"""
    try:
        _send_email_sync(order_id, event_type)
    except Exception as e:
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_sms(self, order_id, event_type):
    """Send order-related SMS notification (Celery task)"""
    try:
        _send_sms_sync(order_id, event_type)
    except Exception as e:
        raise self.retry(exc=e)


def _is_redis_available():
    """Quick check if Redis is available"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1)
        r.ping()
        return True
    except:
        return False


@shared_task
def send_order_notifications(order_id, event_type):
    """
    Trigger both email and SMS notifications
    
    Automatically falls back to synchronous mode if Redis/Celery unavailable.
    This ensures notifications are still sent even without background workers.
    """
    # Check if Redis is available before attempting async
    if _is_redis_available():
        try:
            # Try async (requires Redis + Celery worker)
            send_order_email.delay(order_id, event_type)
            send_order_sms.delay(order_id, event_type)
            logger.info(f"✓ Queued notifications (async) for order {order_id}: {event_type}")
            return
        except Exception as e:
            logger.warning(f"Async sending failed, trying sync: {str(e)[:100]}")
    
    # Fallback to synchronous mode (works without Redis)
    logger.info(f"Sending notifications synchronously for order {order_id}: {event_type}")
    
    try:
        _send_email_sync(order_id, event_type)
    except Exception as email_err:
        logger.error(f"Sync email failed: {str(email_err)}")
    
    try:
        _send_sms_sync(order_id, event_type)
    except Exception as sms_err:
        logger.error(f"Sync SMS failed: {str(sms_err)}")
