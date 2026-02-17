# Quick Razorpay Setup Guide

## ⚡ Quick Fix (5 Minutes)

Your payment system is almost ready! You just need to add Razorpay test credentials.

### Option 1: Use Test Credentials (Recommended for Development)

**Step 1:** Get your FREE test credentials:
1. Visit https://dashboard.razorpay.com/signup
2. Sign up (takes 2 minutes)
3. Go to Settings → API Keys → "Test Mode"
4. Click "Generate Test Key"
5. Copy your **Key ID** (starts with `rzp_test_`)  
6. Copy your **Key Secret**

**Step 2:** Update `certibuy/settings.py`:

Find lines with `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` and replace them with:

```python
# Razorpay Payment Gateway
RAZORPAY_KEY_ID = 'rzp_test_YOUR_KEY_ID_HERE'
RAZORPAY_KEY_SECRET = 'YOUR_SECRET_KEY_HERE'
```

**Step 3:** Restart your Django server:
```bash
# Stop the current server (Ctrl+C)
# Then restart
python manage.py runserver
```

**Step 4:** Test the payment:
1. Go to checkout
2. Click "Place Order"
3. Use these test card details:
   - **Card Number:** 4111 1111 1111 1111
   - **CVV:** 123
   - **Expiry:** Any future date
   - **Name:** Test User

✅ **Done! Your payment system is now working!**

---

## Option 2: Use Environment Variables (Production Best Practice)

**For Windows (PowerShell):**
```powershell
$env:RAZORPAY_KEY_ID = "rzp_test_YOUR_KEY_ID"
$env:RAZORPAY_KEY_SECRET = "YOUR_SECRET_KEY"
python manage.py runserver
```

**For Linux/Mac:**
```bash
export RAZORPAY_KEY_ID="rzp_test_YOUR_KEY_ID"
export RAZORPAY_KEY_SECRET="YOUR_SECRET_KEY"
python manage.py runserver
```

---

## 🧪 Test Cards (Razorpay Test Mode)

| Card Number         | Result  | Description                    |
|---------------------|---------|--------------------------------|
| 4111 1111 1111 1111 | Success | Standard Visa test card        |
| 5555 5555 5555 4444 | Success | Standard Mastercard test card  |
| 4000 0000 0000 0002 | Failed  | Card declined                  |

**For UPI Testing:**
- Use `success@razorpay` - Payment succeeds
- Use `failure@razorpay` - Payment fails

---

## ✅ Verify Installation

Run this test:
```bash
python manage.py shell
```

Then paste:
```python
from django.conf import settings
print("Key ID:", settings.RAZORPAY_KEY_ID)
print("Key Secret:", settings.RAZORPAY_KEY_SECRET[:10] + "...")

from orders.views import get_razorpay_client
client = get_razorpay_client()
if client:
    print("✓ Razorpay client initialized successfully!")
else:
    print("✗ Failed - Check your credentials")
```

---

## 🚀 Going Live (Production)

When ready to accept real payments:

1. **Complete KYC** on Razorpay dashboard
2. **Get Live Keys** (Settings → API Keys → Live Mode)
3. **Update settings** with `rzp_live_` keys
4. **Enable webhook** for payment verification
5. **Test thoroughly** before going live

---

## 📞 Need Help?

- Razorpay Docs: https://razorpay.com/docs/
- API Keys Guide: https://razorpay.com/docs/payments/dashboard/account-settings/api-keys/
- Test Cards: https://razorpay.com/docs/payments/payments/test-card-details/

---

**Quick Tip:** Keep your test credentials in settings during development. Move to environment variables before deploying to production!
