# CertiBuy Razorpay Integration - ACTIVATION GUIDE

**Status:** Implementation Complete ✅  
**Ready for:** Production Deployment  
**Estimated Setup Time:** 10 minutes

---

## 🎯 YOUR NEXT STEPS (10 Minutes to Live Payments)

### Step 1: Get Razorpay Live Credentials (3 minutes)

1. Visit: https://dashboard.razorpay.com
2. Login with your email
3. Complete KYC verification (if not done)
4. Go to **Settings → API Keys**
5. Switch to **LIVE MODE** (not test mode)
6. Copy these two values:

```
RAZORPAY_KEY_ID = rzp_live_XXXXXXXXXXXXXXXX
RAZORPAY_KEY_SECRET = XXXXXXXXXXXXXXXX
```

⚠️ **IMPORTANT:** Keep SECRET key private - Never commit to Git

### Step 2: Set Environment Variables (3 minutes)

**Option A: Using .env file**
```bash
# Create/edit .env file in project root
cat > /path/to/cirtibuy/.env << EOF
RAZORPAY_KEY_ID=rzp_live_XXXXXXXXXXXXXXXX
RAZORPAY_KEY_SECRET=XXXXXXXXXXXXXXXX
EOF

chmod 600 .env
```

**Option B: System Environment (Recommended for Production)**
```bash
# SSH to production server
export RAZORPAY_KEY_ID="rzp_live_XXXXXXXXXXXXXXXX"
export RAZORPAY_KEY_SECRET="XXXXXXXXXXXXXXXX"

# Make persistent (add to ~/.bashrc or systemd service)
```

**Option C: Docker/Systemd**
```bash
# In systemd service file
[Service]
Environment="RAZORPAY_KEY_ID=rzp_live_XXXXXXXXXXXXXXXX"
Environment="RAZORPAY_KEY_SECRET=XXXXXXXXXXXXXXXX"
```

### Step 3: Verify Integration (2 minutes)

```bash
# Navigate to project directory
cd /path/to/cirtibuy

# Activate virtual environment
source .venv/bin/activate

# Run verification script
python verify_payment_production.py
```

**Expected Output:**
```
✅ PASS: Environment Variables
✅ PASS: Razorpay SDK
✅ PASS: Signature Verification
✅ PASS: Payment Flow
✅ PASS: Payment Views
✅ PASS: CSRF Protection
✅ PASS: Database
✅ PASS: HTTPS/SSL
✅ ALL 8 CHECKS PASSED - PRODUCTION READY
```

If any check fails →  see **TROUBLESHOOTING** section below

### Step 4: Restart Django (1 minute)

**Development Server:**
```bash
# Stop current server
pkill -f "python manage.py runserver"

# Start with new credentials
python manage.py runserver 0.0.0.0:8000
```

**Production (Systemd):**
```bash
sudo systemctl restart certibuy
```

**Production (Supervisor):**
```bash
sudo supervisorctl restart certibuy
```

### Step 5: Test Payment (1 minute)

**In Browser:**

1. Go to: `https://yourdomain.com`
2. Login as customer
3. Add any product to cart
4. Proceed to **Checkout**
5. Complete **Step 1** (Address) - click "Continue"
6. Complete **Step 2** (Payment) - select **"Online Payment"** - click "Continue"
7. Review **Step 3** (Order)
8. Click **"Place Order"**
9. Razorpay popup appears
10. Use test card (in test mode) or your card (in live mode):
    - **Card Number:** 4111 1111 1111 1111
    - **Expiry:** 12/25 (or any future date)
    - **CVV:** 123 (or any 3 digits)
11. Click **Pay**
12. ✅ See "Payment Successful!" message
13. ✅ Redirected to confirmation page

**In Django Admin:**

1. Go to: `https://yourdomain.com/admin/orders/order/`
2. Find your test order
3. Verify these fields:
   - `payment_status` = "success" ✅
   - `razorpay_order_id` = populated ✅
   - `razorpay_payment_id` = populated ✅
   - `status` = "confirmed" ✅

---

## 🔍 TROUBLESHOOTING

### Issue: "Razorpay key not configured" or "Payment gateway not properly configured"

**Cause:** Environment variables not set

**Solution:**
```bash
# Verify environment variables are set
echo $RAZORPAY_KEY_ID
echo $RAZORPAY_KEY_SECRET

# If empty:
export RAZORPAY_KEY_ID="rzp_live_XXXXXXXXXXXXXXXX"
export RAZORPAY_KEY_SECRET="XXXXXXXXXXXXXXXX"

# Restart Django
systemctl restart certibuy
```

### Issue: verify_payment_production.py shows FAILED checks

**Solution:** Address each failed check:

```
❌ FAIL: Environment Variables
→ Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET

❌ FAIL: Razorpay SDK
→ pip install razorpay>=1.4.2

❌ FAIL: HTTPS/SSL
→ Install SSL certificate, enable SECURE_SSL_REDIRECT

❌ FAIL: Database
→ python manage.py migrate orders
```

### Issue: Payment shows "Payment verification failed"

**Cause 1:** Network timeout
- **Solution:** Retry payment

**Cause 2:** Signature mismatch (tampering detected)
- **Solution:** Check logs: `tail -f logs/error.log`

**Cause 3:** Amount mismatch
- **Solution:** Don't modify order amount after creating razorpay_order_id

### Issue: Order not confirmed after successful Razorpay payment

**Cause 1:** Payment callback webhook not received
- **Solution:** Check Razorpay dashboard → Webhooks

**Cause 2:** Network timeout on callback
- **Solution:** Wait 30 seconds, reload page

**Cause 3:** Signature verification failed
- **Solution:** Check logs for [FRAUD_ALERT]

---

## 📊 WHAT'S ALREADY IMPLEMENTED

You don't need to do anything for these - they're already active:

### Backend Security
- ✅ Server-side signature verification (HMAC-SHA256)
- ✅ Amount verification (Razorpay API)
- ✅ Idempotency protection (no duplicate payments)
- ✅ Atomic transactions (all-or-nothing)
- ✅ CSRF protection (on all POST endpoints)
- ✅ Input validation (all fields validated)
- ✅ Audit logging (complete payment trail)

### Database Security
- ✅ Unique constraints on payment IDs
- ✅ No sensitive data stored
- ✅ Payment status tracking
- ✅ Order status history

### Frontend Security
- ✅ Official Razorpay popup (NOT manual form)
- ✅ CSRF token validation
- ✅ Client-side validation
- ✅ Comprehensive error messages
- ✅ Console logging for debugging

### Configuration
- ✅ Environment variables for credentials
- ✅ Settings configured from .env
- ✅ Production-grade error handling
- ✅ Complete documentation

---

## 📈 MONITORING AFTER DEPLOYMENT

### Daily Checks

```bash
# Check for errors
tail -f logs/error.log
grep -i "payment" logs/error.log

# Monitor successful payments
grep "\[PAYMENT\]" logs/debug.log

# Check for fraud alerts
grep "\[FRAUD_ALERT\]" logs/debug.log
```

### Weekly Metrics

**In Django Admin:**
```
Orders → Order
Filter by: created_at >= last week

Select all, check:
- Count with payment_status='success' (should be high)
- Count with payment_status='failed' (should be low)
- Count with payment_status='pending' (should be near zero)
```

### Monthly Report

```python
# Django shell: python manage.py shell

from orders.models import Order
from datetime import timedelta
from django.utils import timezone

# Payment stats for last 30 days
month_ago = timezone.now() - timedelta(days=30)
orders = Order.objects.filter(
    payment_method='online',
    created_at__gte=month_ago
)

total = orders.count()
success = orders.filter(payment_status='success').count()
failed = orders.filter(payment_status='failed').count()
pending = orders.filter(payment_status='pending').count()

success_rate = (success / total * 100) if total > 0 else 0

print(f"Total Orders: {total}")
print(f"Successful: {success} ({success_rate:.1f}%)")
print(f"Failed: {failed}")
print(f"Pending: {pending}")
```

---

## 🚀 LIVE vs TEST MODE

### Test Mode (Development)
```
RAZORPAY_KEY_ID = rzp_test_XXXXXXXXXXXXXXXX
Test Card: 4111 1111 1111 1111
Result: No real money charged
```

### Live Mode (Production)
```
RAZORPAY_KEY_ID = rzp_live_XXXXXXXXXXXXXXXX
Real Cards: Use customer's actual card
Result: Real money charged (₹1 minimum)
```

**To Switch:**
1. Go to: https://dashboard.razorpay.com/app/dashboard#/website/settings/api-keys
2. Switch to LIVE tab
3. Copy new keys
4. Update environment variables
5. Restart Django

---

## ✅ FINAL CHECKLIST BEFORE GOING LIVE

- [ ] Razorpay account created and KYC verified
- [ ] Live API keys obtained (rzp_live_*...)
- [ ] Environment variables set (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
- [ ] Django restarted
- [ ] verify_payment_production.py passed
- [ ] Test payment successful (card 4111 1111 1111 1111)
- [ ] Order confirmed in admin (payment_status='success')
- [ ] Email notification sent
- [ ] SSL/HTTPS working
- [ ] Logs monitored (no [FRAUD_ALERT] entries)
- [ ] Team trained on payment process
- [ ] Backup procedures in place
- [ ] Error monitoring configured (Sentry, etc.)

---

## 📖 DOCUMENTATION

After activation, refer to these for troubleshooting:

| Document | When to Use |
|----------|------------|
| `PAYMENT_PRODUCTION_SECURITY.md` | Technical deep dive, security audit |
| `RAZORPAY_DEPLOYMENT_GUIDE.md` | Deployment steps, operations |
| `PAYMENT_UPGRADE_SUMMARY.md` | Overview of changes made |
| `verify_payment_production.py` | Automated verification |

---

## 🎉 YOU'RE READY!

The hard work is done. All you need to do is:

1. **Get credentials** (3 min) → https://dashboard.razorpay.com
2. **Set environment** (3 min) → `export RAZORPAY_KEY_ID=...`
3. **Verify** (2 min) → `python verify_payment_production.py`
4. **Restart Django** (1 min) → `systemctl restart certibuy`
5. **Test** (1 min) → Add to cart, checkout, pay with test card

**Total: 10 minutes to live secure payments** ✅

---

## 💬 SUPPORT

**If verification fails:**
1. Check the specific error message
2. Refer to **TROUBLESHOOTING** section above
3. Check `PAYMENT_PRODUCTION_SECURITY.md` for technical details
4. Run verification script with more details:
   ```bash
   python verify_payment_production.py 2>&1 | tee verification_log.txt
   ```

**Contact:**
- Razorpay Support: support@razorpay.com
- Your Dev Team: [contact-info]

---

**Ready to start accepting payments?** Just follow the 5 steps above! ✅

Last Updated: 2026-02-17
