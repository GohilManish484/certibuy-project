from django.contrib import admin
from django.utils import timezone
from .models import Order, OrderItem, OrderStatusHistory, NotificationLog, WarrantyPlan
from .tasks import send_order_notifications
import logging

logger = logging.getLogger(__name__)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'get_total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_number', 'user', 'total_amount', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'razorpay_order_id']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at', 'order_number', 'razorpay_order_id', 
                      'razorpay_payment_id', 'razorpay_signature']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'order_number', 'status', 'payment_status', 'payment_method')
        }),
        ('Payment Details', {
            'fields': ('total_amount', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('Shipping Info', {
            'fields': ('address', 'tracking_id')
        }),
        ('Refund Info', {
            'fields': ('refund_id', 'refund_status', 'refund_amount', 'refunded_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'cancelled_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save_model to trigger notifications on status change"""
        if change:  # Only for updates
            old_obj = Order.objects.get(pk=obj.pk)
            old_status = old_obj.status
            new_status = obj.status
            
            # Save the order first
            super().save_model(request, obj, form, change)
            
            # Trigger notifications based on status change
            if old_status != new_status:
                # Create status history
                OrderStatusHistory.objects.create(
                    order=obj,
                    status=new_status,
                    updated_by=request.user,
                    notes=f"Status changed from {old_status} to {new_status} by admin"
                )
                
                # Trigger appropriate notification
                notification_map = {
                    'shipped': 'order_shipped',
                    'out_for_delivery': 'out_for_delivery',
                    'delivered': 'order_delivered',
                }
                
                event_type = notification_map.get(new_status)
                if event_type:
                    try:
                        send_order_notifications.delay(obj.id, event_type)
                        logger.info(f"Queued {event_type} notification for order {obj.order_number}")
                    except Exception as e:
                        logger.error(f"Failed to queue notification: {str(e)}")
        else:
            super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price', 'get_total_price']
    list_filter = ['order__status']
    search_fields = ['product__name', 'order__user__username']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'updated_by', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['order__order_number', 'order__user__username']
    readonly_fields = ['order', 'status', 'updated_by', 'notes', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'notification_type', 'event_type', 'recipient', 'status', 'sent_at', 'created_at']
    list_filter = ['notification_type', 'status', 'event_type', 'created_at']
    search_fields = ['recipient', 'user__username', 'order__order_number']
    readonly_fields = ['user', 'order', 'notification_type', 'event_type', 'recipient', 
                      'status', 'response_log', 'error_message', 'retry_count', 'sent_at', 'created_at']
    
    fieldsets = (
        ('Notification Info', {
            'fields': ('user', 'order', 'notification_type', 'event_type', 'recipient')
        }),
        ('Status', {
            'fields': ('status', 'retry_count', 'sent_at', 'created_at')
        }),
        ('Response Details', {
            'fields': ('response_log', 'error_message'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(WarrantyPlan)
class WarrantyPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration_months', 'price', 'accidental_damage_covered', 'is_active', 'display_order']
    list_filter = ['is_active', 'accidental_damage_covered']
    search_fields = ['name']
    list_editable = ['is_active', 'display_order']
    ordering = ['display_order', 'duration_months']
    
    fieldsets = (
        ('Plan Details', {
            'fields': ('name', 'duration_months', 'price')
        }),
        ('Coverage', {
            'fields': ('coverage_details', 'accidental_damage_covered')
        }),
        ('Status', {
            'fields': ('is_active', 'display_order')
        }),
    )
