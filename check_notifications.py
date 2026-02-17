import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certibuy.settings')
django.setup()

from orders.models import Order, NotificationLog

print("=" * 60)
print("ORDER AND NOTIFICATION STATUS CHECK")
print("=" * 60)

# Check orders
total_orders = Order.objects.count()
print(f"\nTotal Orders: {total_orders}")

if total_orders > 0:
    print("\nRecent Orders:")
    orders = Order.objects.select_related('user', 'address').order_by('-created_at')[:5]
    for o in orders:
        print(f"\n  Order: {o.order_number}")
        print(f"  Status: {o.status}")
        print(f"  Email: {o.user.email}")
        print(f"  Phone: {o.address.phone if o.address else 'NO ADDRESS'}")
        print(f"  Created: {o.created_at}")
        
        # Check notifications for this order
        notifications = NotificationLog.objects.filter(order=o)
        print(f"  Notifications sent: {notifications.count()}")
        for notif in notifications:
            print(f"    - {notif.event_type} ({notif.notification_type}): {notif.status}")

# Check notification logs
total_notifications = NotificationLog.objects.count()
print(f"\n\nTotal Notifications: {total_notifications}")

if total_notifications > 0:
    print("\nRecent Notifications:")
    recent = NotificationLog.objects.select_related('order').order_by('-created_at')[:10]
    for n in recent:
        print(f"  {n.created_at}: {n.event_type} ({n.notification_type}) - {n.status}")
        if n.status == 'failed':
            print(f"    Error: {n.error_message}")
else:
    print("\n⚠️  NO NOTIFICATIONS FOUND!")
    print("This means notifications are not being sent.")
    
print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)

# Check if Redis is running
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print("✓ Redis is running")
except:
    print("✗ Redis is NOT running - notifications won't be sent!")
    print("  Solution: Install and start Redis")
    print("  Download: https://github.com/microsoftarchive/redis/releases")

# Check environment
from django.conf import settings
if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
    print("✓ Email credentials configured")
else:
    print("✗ Email credentials NOT configured in .env")

if settings.MSG91_API_KEY or settings.FAST2SMS_API_KEY:
    print(f"✓ SMS configured ({settings.SMS_PROVIDER})")
else:
    print("✗ SMS credentials NOT configured in .env")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("1. Start Redis server")
print("2. Start Celery worker:")
print("   celery -A certibuy worker --loglevel=info --pool=solo")
print("3. Place a test order")
print("4. Check this script again to see notifications")
print("=" * 60)
