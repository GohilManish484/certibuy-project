from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.crypto import get_random_string
from products.models import Product
from datetime import timedelta

User = get_user_model()

def generate_order_number():
    """Generate unique order number"""
    import secrets
    return f"ORD-{int(timezone.now().timestamp())}-{secrets.randbelow(10000):04d}"


class WarrantyPlan(models.Model):
    name = models.CharField(max_length=200)
    duration_months = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    coverage_details = models.JSONField(default=list)
    accidental_damage_covered = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'duration_months']
    
    def __str__(self):
        return f"{self.name} - {self.duration_months} months"


class OrderAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_addresses')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-updated_at']

    def __str__(self):
        return f"{self.full_name} - {self.address[:50]}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('payment_successful', 'Payment Successful'),
        ('confirmed', 'Confirmed'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online Payment'),
        ('emi', 'EMI'),
        ('cod', 'Cash on Delivery'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cod_pending', 'COD Pending'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True, db_index=True, null=True, blank=True, default=None)
    address = models.ForeignKey(OrderAddress, on_delete=models.PROTECT, related_name='orders', null=True, blank=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    warranty_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    selected_warranty_plan = models.ForeignKey('WarrantyPlan', on_delete=models.PROTECT, null=True, blank=True, related_name='orders')
    warranty_expiry_date = models.DateField(null=True, blank=True)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='online')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    
    emi_plan = models.CharField(max_length=50, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending_payment')
    
    tracking_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    courier_name = models.CharField(max_length=100, blank=True, null=True)
    
    refund_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    refund_status = models.CharField(max_length=20, blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    estimated_delivery = models.DateField(blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def can_cancel(self):
        return self.status in ['pending_payment', 'payment_successful', 'confirmed', 'packed', 'shipped', 'out_for_delivery']
    
    def can_request_refund(self):
        return self.status == 'delivered' and self.payment_method != 'cod'


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.ORDER_STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Order Status Histories'
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=50, blank=True, null=True)
    storage = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    warranty_included = models.BooleanField(default=True)
    extended_warranty_plan = models.ForeignKey('WarrantyPlan', on_delete=models.PROTECT, null=True, blank=True, related_name='order_items')
    warranty_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    warranty_expiry_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} - Order #{self.order.id}"
    
    def get_total_price(self):
        return self.price * self.quantity


class NotificationLog(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE_CHOICES)
    event_type = models.CharField(max_length=50)
    recipient = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    response_log = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.PositiveIntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'notification_type']),
            models.Index(fields=['order', 'event_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.notification_type.upper()} - {self.event_type} - {self.status}"
