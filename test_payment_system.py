#!/usr/bin/env python
"""
Test script to diagnose payment gateway issues
Run: python manage.py shell < test_payment_system.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certibuy.settings')
django.setup()

from django.conf import settings
from orders.views import get_razorpay_client
import logging

logger = logging.getLogger(__name__)

print("\n" + "="*60)
print("PAYMENT SYSTEM DIAGNOSTIC TEST")
print("="*60 + "\n")

# Test 1: Check Razorpay credentials
print("1. RAZORPAY CREDENTIALS CHECK")
print("-" * 60)
razorpay_key_id = settings.RAZORPAY_KEY_ID
razorpay_key_secret = settings.RAZORPAY_KEY_SECRET

print(f"   RAZORPAY_KEY_ID: {razorpay_key_id[:20]}..." if razorpay_key_id else "   RAZORPAY_KEY_ID: NOT SET")
print(f"   RAZORPAY_KEY_SECRET: {'*' * 20}..." if razorpay_key_secret else "   RAZORPAY_KEY_SECRET: NOT SET")

if not razorpay_key_id or not razorpay_key_secret:
    print("\n   ❌ ERROR: Razorpay credentials are missing!")
    print("   SET: RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET environment variables")
else:
    if 'rzp_test' in razorpay_key_id or 'test' in str(razorpay_key_id).lower():
        print("   ✓ Test credentials detected (development mode)")
    else:
        print("   ✓ Production credentials detected")

# Test 2: Check Razorpay SDK
print("\n2. RAZORPAY SDK CHECK")
print("-" * 60)
try:
    import razorpay
    print(f"   ✓ Razorpay SDK installed: v{razorpay.__version__ if hasattr(razorpay, '__version__') else 'unknown'}")
except ImportError:
    print("   ❌ ERROR: Razorpay SDK not installed!")
    print("   Install: pip install razorpay")
    sys.exit(1)

# Test 3: Check Razorpay client
print("\n3. RAZORPAY CLIENT TEST")
print("-" * 60)
client = get_razorpay_client()
if client:
    print("   ✓ Razorpay client initialized successfully")
else:
    print("   ❌ ERROR: Failed to initialize Razorpay client")
    print("   Check your credentials are correctly set")

# Test 4: Try to create a test order
print("\n4. TEST ORDER CREATION")
print("-" * 60)
if client:
    try:
        test_order = client.order.create({
            'amount': 100,  # 1 INR in paise
            'currency': 'INR',
            'receipt': 'test-001',
        })
        print(f"   ✓ Test order created: {test_order['id']}")
        print(f"   Amount: ₹{test_order['amount'] / 100}")
        print(f"   Status: {test_order['status']}")
    except Exception as e:
        print(f"   ❌ ERROR: Order creation failed")
        print(f"   Message: {str(e)}")
else:
    print("   ⊘ Skipped: Razorpay client not available")

# Test 5: Database check
print("\n5. DATABASE CHECK")
print("-" * 60)
from orders.models import Order
try:
    order_count = Order.objects.count()
    print(f"   ✓ Database accessible")
    print(f"   Total orders: {order_count}")
except Exception as e:
    print(f"   ❌ ERROR: Database error")
    print(f"   Message: {str(e)}")

# Test 6: Settings check
print("\n6. PAYMENT SETTINGS CHECK")
print("-" * 60)
print(f"   CSRF Trusted Origins: {settings.CSRF_TRUSTED_ORIGINS if hasattr(settings, 'CSRF_TRUSTED_ORIGINS') else 'Not configured'}")
print(f"   Debug Mode: {settings.DEBUG}")
print(f"   Allowed Hosts: {settings.ALLOWED_HOSTS}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

if razorpay_key_id and razorpay_key_secret and client:
    print("\n✓ All checks passed! Payment system should be working.\n")
else:
    print("\n❌ Some issues detected. Please fix:")
    if not razorpay_key_id or not razorpay_key_secret:
        print("   - Set RAZORPAY_KEY_ID environment variable")
        print("   - Set RAZORPAY_KEY_SECRET environment variable")
    if not client:
        print("   - Verify Razorpay credentials are correct")
    print()

print("="*60 + "\n")
