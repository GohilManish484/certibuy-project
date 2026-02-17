#!/usr/bin/env python
"""Quick Razorpay Configuration Test"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certibuy.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.conf import settings
from orders.views import get_razorpay_client

print("=" * 60)
print("RAZORPAY CONFIGURATION TEST")
print("=" * 60)

# Test 1: Check if credentials are set
print("\n1. CHECKING CREDENTIALS...")
print("-" * 60)
key_id = settings.RAZORPAY_KEY_ID
key_secret = settings.RAZORPAY_KEY_SECRET

if not key_id or 'REPLACE_ME' in key_id or 'SAMPLE' in key_id:
    print("❌ RAZORPAY_KEY_ID not configured properly")
    print(f"   Current value: {key_id}")
    print("\n📋 ACTION REQUIRED:")
    print("   1. Get test keys from: https://dashboard.razorpay.com/signup")
    print("   2. Update certibuy/settings.py with your keys")
    print("   3. Or read RAZORPAY_SETUP_QUICK.md for detailed instructions")
    sys.exit(1)
else:
    print(f"✓ RAZORPAY_KEY_ID: {key_id}")

if not key_secret or 'REPLACE_ME' in key_secret or 'SAMPLE' in key_secret:
    print("❌ RAZORPAY_KEY_SECRET not configured properly")
    print(f"   Current value: {key_secret[:20]}...")
    print("\n📋 ACTION REQUIRED:")
    print("   1. Get test keys from: https://dashboard.razorpay.com/signup")
    print("   2. Update certibuy/settings.py with your keys")
    print("   3. Or read RAZORPAY_SETUP_QUICK.md for detailed instructions")
    sys.exit(1)
else:
    print(f"✓ RAZORPAY_KEY_SECRET: {key_secret[:10]}...***")

# Test 2: Check if razorpay package is installed
print("\n2. CHECKING RAZORPAY SDK...")
print("-" * 60)
try:
    import razorpay
    print(f"✓ Razorpay SDK installed (v{razorpay.__version__})")
except ImportError:
    print("❌ Razorpay SDK not installed")
    print("\n📋 ACTION REQUIRED:")
    print("   Run: pip install razorpay>=1.4.2")
    sys.exit(1)

# Test 3: Test client initialization
print("\n3. TESTING CLIENT INITIALIZATION...")
print("-" * 60)
client = get_razorpay_client()
if client:
    print("✓ Razorpay client initialized successfully")
else:
    print("❌ Failed to initialize Razorpay client")
    print("\n📋 ACTION REQUIRED:")
    print("   Check that your credentials are valid")
    print("   Test mode keys should start with 'rzp_test_'")
    sys.exit(1)

# Test 4: Try creating a test order
print("\n4. TESTING API CONNECTION...")
print("-" * 60)
try:
    test_order = client.order.create({
        'amount': 100,  # ₹1.00 in paise
        'currency': 'INR',
        'receipt': 'test-config-check',
    })
    print(f"✓ Successfully connected to Razorpay API")
    print(f"  Test order created: {test_order['id']}")
    print(f"  Amount: ₹{test_order['amount'] / 100:.2f}")
    print(f"  Status: {test_order['status']}")
except Exception as e:
    print(f"❌ API Connection Failed: {str(e)}")
    print("\n📋 POSSIBLE CAUSES:")
    print("   1. Invalid credentials")
    print("   2. Network connectivity issue")
    print("   3. Razorpay API temporarily down")
    sys.exit(1)

# Success!
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nYour Razorpay integration is configured correctly!")
print("\n🧪 TEST CHECKOUT:")
print("   1. Start Django: python manage.py runserver")
print("   2. Add products to cart")
print("   3. Go through checkout")
print("   4. Use test card: 4111 1111 1111 1111")
print("   5. CVV: 123, Expiry: Any future date")
print("\n📖 For more info, see: RAZORPAY_SETUP_QUICK.md")
print("=" * 60)
