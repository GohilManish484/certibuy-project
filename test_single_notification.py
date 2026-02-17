"""Test notification sending on existing order"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certibuy.settings')
django.setup()

from orders.tasks import send_order_notifications
from orders.models import Order

# Get the latest order
latest_order = Order.objects.select_related('user', 'address').order_by('-created_at').first()

if latest_order:
    print(f"Testing notifications for order: {latest_order.order_number}")
    print(f"Customer: {latest_order.user.get_full_name() or latest_order.user.username}")
    print(f"Email: {latest_order.user.email}")
    print(f"Phone: {latest_order.address.phone if latest_order.address else 'NO ADDRESS'}")
    print("\nSending notifications...")
    print("-" * 60)
    
    try:
        # This will automatically use sync mode since Redis is not running
        send_order_notifications(latest_order.id, 'order_confirmed')
        print("\n✓ Notifications sent successfully!")
        print("\nCheck:")
        print("1. Email inbox:", latest_order.user.email)
        if latest_order.address and latest_order.address.phone:
            print("2. SMS on phone:", latest_order.address.phone)
        print("3. Admin panel: Notification Logs")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("No orders found in database")
