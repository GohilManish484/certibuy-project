import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Notification
from orders.models import Order
from inspections.models import Inspection
from products.models import Product

logger = logging.getLogger(__name__)


def _create_notification(title, message, notif_type, priority='medium', related_order=None, created_by='system'):
    try:
        Notification.objects.create(
            title=title,
            message=message,
            type=notif_type,
            priority=priority,
            related_order=related_order,
            created_by=created_by,
        )
    except Exception as exc:
        logger.error("Failed to create notification: %s", str(exc))


@receiver(pre_save, sender=Order)
def _cache_order_previous_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_state = None
        return
    try:
        instance._previous_state = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        instance._previous_state = None


@receiver(post_save, sender=Order)
def _order_notifications(sender, instance, created, **kwargs):
    if created:
        title = "New Order Placed"
        order_ref = instance.order_number or f"#{instance.id}"
        message = f"A new order was placed: {order_ref}."
        _create_notification(title, message, 'order', 'medium', instance)
        return

    previous = getattr(instance, '_previous_state', None)
    if not previous:
        return

    if previous.payment_status != instance.payment_status:
        if instance.payment_status == 'success':
            title = "Payment Successful"
            message = f"Payment succeeded for order {instance.order_number or instance.id}."
            _create_notification(title, message, 'payment', 'medium', instance)
        elif instance.payment_status == 'failed':
            title = "Payment Failed"
            message = f"Payment failed for order {instance.order_number or instance.id}."
            _create_notification(title, message, 'payment', 'high', instance)
        elif instance.payment_status == 'refunded':
            title = "Refund Processed"
            message = f"Refund processed for order {instance.order_number or instance.id}."
            _create_notification(title, message, 'refund', 'medium', instance)

    if previous.status != instance.status:
        if instance.status == 'cancelled':
            title = "Order Cancelled"
            message = f"Order {instance.order_number or instance.id} was cancelled."
            _create_notification(title, message, 'order', 'medium', instance)
            if instance.payment_method == 'online':
                title = "Refund Requested"
                message = f"Refund requested for order {instance.order_number or instance.id}."
                _create_notification(title, message, 'refund', 'medium', instance)
        elif instance.status == 'shipped':
            title = "Order Shipped"
            message = f"Order {instance.order_number or instance.id} was shipped."
            _create_notification(title, message, 'order', 'medium', instance)

    if previous.refund_id is None and instance.refund_id:
        title = "Refund Requested"
        message = f"Refund requested for order {instance.order_number or instance.id}."
        _create_notification(title, message, 'refund', 'medium', instance)

    if previous.refund_status != instance.refund_status and instance.refund_status:
        if instance.refund_status in {'processed', 'success', 'completed'}:
            title = "Refund Processed"
            message = f"Refund processed for order {instance.order_number or instance.id}."
            _create_notification(title, message, 'refund', 'medium', instance)


@receiver(pre_save, sender=Inspection)
def _cache_inspection_previous_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_state = None
        return
    try:
        instance._previous_state = Inspection.objects.get(pk=instance.pk)
    except Inspection.DoesNotExist:
        instance._previous_state = None


@receiver(post_save, sender=Inspection)
def _inspection_notifications(sender, instance, created, **kwargs):
    previous = getattr(instance, '_previous_state', None)
    if previous and previous.status == instance.status:
        return

    if instance.status == 'completed':
        title = "Inspection Report Submitted"
        subject = instance.submission.product_name
        message = f"Inspection report submitted for {subject}."
        _create_notification(title, message, 'inspection', 'medium')


@receiver(pre_save, sender=Product)
def _cache_product_previous_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_state = None
        return
    try:
        instance._previous_state = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        instance._previous_state = None


@receiver(post_save, sender=Product)
def _product_stock_notifications(sender, instance, created, **kwargs):
    previous = getattr(instance, '_previous_state', None)
    threshold = instance.low_stock_threshold

    if created:
        if instance.stock_quantity <= threshold:
            title = "Low Stock Detected"
            message = f"Low stock for {instance.name} (qty: {instance.stock_quantity})."
            _create_notification(title, message, 'inventory', 'high')
        return

    if previous and previous.stock_quantity > threshold and instance.stock_quantity <= threshold:
        title = "Low Stock Detected"
        message = f"Low stock for {instance.name} (qty: {instance.stock_quantity})."
        _create_notification(title, message, 'inventory', 'high')
