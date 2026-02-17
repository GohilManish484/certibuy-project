# Payment System - Quick Setup Guide

## What Was Fixed

✅ **Enhanced Payment Gateway Template**  
- Improved error handling with detailed messages
- Better CSRF token validation
- Loading states and user feedback
- Console logging for debugging

✅ **Improved Order Processing**  
- Better error messages for users
- Enhanced logging for debugging
- Proper transaction handling
- Validation at each step

✅ **Diagnostic Tools**  
- Created `test_payment_system.py` to diagnose issues
- Payment flow documentation
- Troubleshooting guides

---

## Step 1: Get Razorpay Credentials

1. Go to https://dashboard.razorpay.com
2. Sign up or log in
3. Navigate to **Settings → API Keys**
4. Copy your **Key ID** and **Key Secret**

### Test Keys (for development)
- Key ID: `rzp_test_xxxxxxxxxxxxx`
- Key Secret: `xxxxxxxxxxxxxxxxxxxxx`

### Live Keys (for production)
- Key ID: `rzp_live_xxxxxxxxxxxxx`  
- Key Secret: `xxxxxxxxxxxxxxxxxxxxx`

---

## Step 2: Set Environment Variables

### On Windows (PowerShell)
```powershell
$env:RAZORPAY_KEY_ID="rzp_test_xxxxxxxxxxxxx"
$env:RAZORPAY_KEY_SECRET="xxxxxxxxxxxxxxxxxxxxx"
```

### On Windows (Command Prompt)
```cmd
set RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
set RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
```

### On Windows (Permanent - Environment Variables GUI)
1. Right-click "This PC" → Properties
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Click "New" under User variables
5. Variable name: `RAZORPAY_KEY_ID`
6. Variable value: `rzp_test_xxxxxxxxxxxxx`
7. Click OK and repeat for `RAZORPAY_KEY_SECRET`
8. Restart terminal/IDE

### On Linux/Mac
```bash
export RAZORPAY_KEY_ID="rzp_test_xxxxxxxxxxxxx"
export RAZORPAY_KEY_SECRET="xxxxxxxxxxxxxxxxxxxxx"
```

---

## Step 3: Verify Installation

### Install Razorpay SDK
```bash
pip install razorpay>=1.4.2
```

### Run Diagnostic Test
```bash
python manage.py shell
```

Then paste this:
```python
from django.conf import settings
from orders.views import get_razorpay_client

print(f"RAZORPAY_KEY_ID: {settings.RAZORPAY_KEY_ID}")
print(f"RAZORPAY_KEY_SECRET: {settings.RAZORPAY_KEY_SECRET}")

client = get_razorpay_client()
if client:
    print("✓ Client initialized successfully")
    
    # Test order creation
    order = client.order.create({
        'amount': 100,
        'currency': 'INR',
        'receipt': 'test-001'
    })
    print(f"✓ Test order created: {order['id']}")
else:
    print("✗ Failed to initialize client")
```

---

## Step 4: Test Payment Flow

### 1. Add Product to Cart
- Go to Shop
- Add any product to cart
- Proceed to checkout

### 2. Select Address
- Provide delivery address

### 3. Select Payment Method
- **Online Payment** - Instantly process with card/UPI/Net Banking
- **EMI Payment** - Flexible monthly payments
- **COD** - Pay at delivery

### 4. Review & Confirm
- Verify order details
- Click "Place Order"

### 5. Test Payment
Use Razorpay Test Card:
- **Card Number:** 4111 1111 1111 1111
- **Expiry:** Any future date (e.g., 12/25)
- **CVV:** Any 3 digits (e.g., 123)

### 6. Expected Result
- Payment gateway opens
- After successful payment
- Order confirmation page appears
- Order created in database

---

## Troubleshooting

### Problem: "Payment gateway is not properly configured"
**Solution:**
```bash
# Check if variables are set
echo %RAZORPAY_KEY_ID%
echo %RAZORPAY_KEY_SECRET%

# Should output your credentials, not empty
```

### Problem: "Payment button does nothing"
**Solution:**
1. Open Browser Console (F12 → Console)
2. Check for errors
3. Verify Razorpay library loaded:
   - F12 → Network → Search "checkout.razorpay"
   - Should show a successful load

### Problem: "Payment verification failed"
**Solution:**
```bash
# Check Django logs
tail -f logs/error.log

# Look for signature verification errors
grep -i "signature" logs/*.log
```

### Problem: "Order created but payment marked as failed"
**Solution:**
1. Check payment callback in Django logs
2. Verify RAZORPAY_KEY_SECRET matches exactly
3. Check database:
   ```bash
   python manage.py dbshell
   SELECT * FROM orders_order WHERE payment_status='failed';
   ```

---

## Payment Testing Scenarios

### ✓ Test Cases to Verify

| Scenario | Expected Result |
|----------|-----------------|
| Online Payment - Success | Order confirmed, payment verified |
| Online Payment - Failure | Payment failed message shown |
| EMI Payment - 3 Months | Order placed with EMI details |
| EMI Payment - 6 Months | Order placed with interest calculated |
| COD Payment | Order placed, payment pending |
| Payment Timeout | Error message, order not created |
| Missing CSRF Token | Payment verification fails |
| Invalid Signature | Payment marked as failed |

---

## Logs & Debugging

### View Payment Logs
```bash
# All payment-related logs
grep -i "payment\|razorpay" logs/debug.log | tail -100

# Payment errors only
grep -i "error" logs/error.log | grep -i "payment"

# Payment callbacks
grep -i "callback" logs/debug.log
```

### Enable Debug Logging in settings.py
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}
```

---

## Success Indicators

✅ **When working correctly, you should see:**

1. Payment form loads without errors
2. Razorpay modal opens when clicking "Complete Payment"
3. Test card accepted (not declined)
4. Order created in database after payment
5. Order confirmation page appears
6. Email notifications sent (if configured)
7. Order status shows as "confirmed" in admin

---

## Production Checklist

Before going live:

- [ ] Switch to production Razorpay keys
- [ ] Test with small amounts first
- [ ] Set RAZORPAY_KEY_ID (production)
- [ ] Set RAZORPAY_KEY_SECRET (production)
- [ ] Verify SSL certificate on domain
- [ ] Test full payment flow with real card
- [ ] Set up email notifications
- [ ] Monitor logs in production
- [ ] Have support contact info ready (Razorpay)

---

## Support Resources

**Razorpay:**
- Documentation: https://razorpay.com/docs
- Support: support@razorpay.com
- Dashboard: https://dashboard.razorpay.com

**This Application:**
- Diagnostic Script: `python test_payment_system.py`
- Error Logs: `logs/error.log`
- Debug Logs: `logs/debug.log`

---

## Files Modified

✅ `templates/orders/payment_gateway.html` - Enhanced payment form  
✅ `orders/views.py` - Improved error handling  
✅ `test_payment_system.py` - Diagnostic script  
✅ `PAYMENT_SETUP_GUIDE.md` - Detailed guide  

---

**Last Updated:** February 17, 2026
