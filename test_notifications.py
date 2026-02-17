#!/usr/bin/env python
"""
Quick Start Script for CERTIBUY Notification System
Run this to verify your notification setup
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certibuy.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from orders.models import Order, NotificationLog
from orders.tasks import send_order_notifications
import redis


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_email_config():
    print_header("EMAIL CONFIGURATION")
    
    required_settings = {
        'EMAIL_HOST': settings.EMAIL_HOST,
        'EMAIL_PORT': settings.EMAIL_PORT,
        'EMAIL_HOST_USER': settings.EMAIL_HOST_USER,
        'EMAIL_HOST_PASSWORD': '***' if settings.EMAIL_HOST_PASSWORD else None,
        'DEFAULT_FROM_EMAIL': settings.DEFAULT_FROM_EMAIL,
    }
    
    for key, value in required_settings.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value or 'NOT SET'}")
    
    if all(required_settings.values()):
        print("\n  ✅ Email configuration looks good!")
        return True
    else:
        print("\n  ❌ Email configuration incomplete!")
        print("  → Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env")
        return False


def check_sms_config():
    print_header("SMS CONFIGURATION")
    
    provider = getattr(settings, 'SMS_PROVIDER', 'msg91')
    print(f"  Primary Provider: {provider.upper()}")
    
    msg91_key = getattr(settings, 'MSG91_API_KEY', '')
    fast2sms_key = getattr(settings, 'FAST2SMS_API_KEY', '')
    
    print(f"\n  MSG91_API_KEY: {'✓ SET' if msg91_key else '✗ NOT SET'}")
    print(f"  FAST2SMS_API_KEY: {'✓ SET' if fast2sms_key else '✗ NOT SET'}")
    
    if msg91_key or fast2sms_key:
        print("\n  ✅ At least one SMS provider is configured!")
        return True
    else:
        print("\n  ⚠️  No SMS providers configured")
        print("  → Set MSG91_API_KEY or FAST2SMS_API_KEY in .env")
        return False


def check_celery_redis():
    print_header("CELERY & REDIS")
    
    broker_url = settings.CELERY_BROKER_URL
    print(f"  Broker URL: {broker_url}")
    
    try:
        r = redis.from_url(broker_url)
        r.ping()
        print("  ✅ Redis connection successful!")
        return True
    except Exception as e:
        print(f"  ❌ Redis connection failed: {str(e)}")
        print("\n  → Make sure Redis server is running:")
        print("     Windows: redis-server")
        print("     Linux:   sudo service redis-server start")
        print("     Mac:     brew services start redis")
        return False


def test_notification():
    print_header("TEST NOTIFICATION")
    
    # Get the first completed order
    order = Order.objects.filter(status__in=['confirmed', 'delivered']).first()
    
    if not order:
        print("  ⚠️  No orders found to test with")
        print("  → Place an order first, then run this script again")
        return False
    
    print(f"\n  Using Order: {order.order_number}")
    print(f"  Customer: {order.user.username} ({order.user.email})")
    
    try:
        # Queue a test notification
        result = send_order_notifications.delay(order.id, 'order_confirmed')
        print(f"\n  ✅ Notification task queued!")
        print(f"  Task ID: {result.id}")
        print("\n  Check your email and phone for the notification.")
        print("  View logs in the Celery worker terminal.")
        return True
    except Exception as e:
        print(f"\n  ❌ Failed to queue notification: {str(e)}")
        print("  → Make sure Celery worker is running:")
        print("     celery -A certibuy worker --loglevel=info --pool=solo")
        return False


def show_notification_logs():
    print_header("RECENT NOTIFICATION LOGS")
    
    logs = NotificationLog.objects.all()[:10]
    
    if not logs:
        print("  No notifications sent yet.")
        return
    
    print(f"\n  Total Notifications: {NotificationLog.objects.count()}\n")
    
    for log in logs:
        status_icon = "✓" if log.status == 'sent' else "✗" if log.status == 'failed' else "⏳"
        print(f"  {status_icon} {log.notification_type.upper()}: {log.event_type}")
        print(f"     To: {log.recipient}")
        print(f"     Status: {log.status.upper()}")
        if log.error_message:
            print(f"     Error: {log.error_message[:50]}...")
        print()


def main():
    print("\n" + "=" * 70)
    print("  CERTIBUY NOTIFICATION SYSTEM - SETUP VERIFICATION")
    print("=" * 70)
    
    results = {
        'email': check_email_config(),
        'sms': check_sms_config(),
        'redis': check_celery_redis(),
    }
    
    show_notification_logs()
    
    print_header("SUMMARY")
    
    if all(results.values()):
        print("\n  🎉 All systems are configured!")
        print("\n  Next Steps:")
        print("  1. Start Celery worker (if not running):")
        print("     celery -A certibuy worker --loglevel=info --pool=solo")
        print("  2. Start Django server:")
        print("     python manage.py runserver")
        print("  3. Place a test order to trigger notifications")
        
        # Offer to send test notification
        if Order.objects.exists():
            print("\n" + "-" * 70)
            response = input("  Send a test notification now? (y/n): ")
            if response.lower() == 'y':
                test_notification()
    else:
        print("\n  ⚠️  Some configurations are missing:")
        if not results['email']:
            print("     - Email settings")
        if not results['sms']:
            print("     - SMS API keys (optional)")
        if not results['redis']:
            print("     - Redis server")
        print("\n  Please check the messages above and update your .env file")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup check cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
