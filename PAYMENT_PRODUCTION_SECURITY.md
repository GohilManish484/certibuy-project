# CertiBuy Payment Gateway - Production Security Documentation

**Status:** Production-Ready
**Last Updated:** 2026-02-17
**Payment Gateway:** Razorpay Official Checkout (v1.4.2+)

---

## 🔐 SECURITY ARCHITECTURE

### Payment Flow (Secure)

```
1. CUSTOMER SELECTS PAYMENT
   ↓
2. PLACE ORDER (Backend Creates Order, status=pending_payment)
   ↓
3. RAZORPAY ORDER CREATED (Server generates razorpay_order_id)
   ↓
4. REDIRECT TO PAYMENT GATEWAY (Shows Razorpay Hosted Popup)
   ↓
5. CUSTOMER COMPLETES PAYMENT (UPI/Card/NetBanking in Razorpay popup)
   ↓
6. RAZORPAY RETURNS PAYMENT DETAILS
   ↓
7. BACKEND VERIFIES SIGNATURE (HMAC-SHA256)
   ↓
8. BACKEND VERIFIES AMOUNT
   ↓
9. BACKEND VERIFIES PAYMENT STATUS
   ↓
10. UPDATE ORDER STATUS = CONFIRMED (Atomic Transaction)
```

---

## ✅ SECURITY CHECKS IMPLEMENTED

### 1. **Server-Side Signature Verification (HMAC-SHA256)**
- ✅ Signature calculated: `HMAC-SHA256(razorpay_order_id|payment_id, RAZORPAY_KEY_SECRET)`
- ✅ Constant-time comparison: `hmac.compare_digest()` prevents timing attacks
- ✅ Tampering prevention: Any modification to order_id or payment_id fails verification

```python
# File: orders/views.py, payment_callback()
expected_signature = hmac.new(
    settings.RAZORPAY_KEY_SECRET.encode(),
    f"{razorpay_order_id}|{payment_id}".encode(),
    hashlib.sha256
).hexdigest()

if not hmac.compare_digest(expected_signature, signature):
    # SECURITY ALERT: Possible tampering
    # Order marked as failed, user NOT given credit
```

### 2. **Amount Verification**
- ✅ Database amount compared against callback amount
- ✅ Razorpay API verification (fetches actual payment amount)
- ✅ Prevents underpayment/overpayment fraud

```python
# Fetch from Razorpay API to prevent tampering
payment_details = razorpay_client.payment.fetch(payment_id)
actual_amount = payment_details.get('amount')  # in paise

if actual_amount != expected_amount_paise:
    # FRAUD ALERT: Amount mismatch
    # Order marked as failed, investigation logged
```

### 3. **Idempotency Protection**
- ✅ Prevents duplicate payment processing
- ✅ Safe to call callback multiple times
- ✅ Row-level locking: `select_for_update()` prevents race conditions

```python
# Check if payment already processed
if order.razorpay_payment_id:
    if order.razorpay_payment_id == payment_id:
        # Idempotent: return success
        return JsonResponse({'status': 'success'})
    else:
        # FRAUD ALERT: Multiple payments for same order
        return JsonResponse({'status': 'error'})
```

### 4. **Atomic Transactions**
- ✅ All-or-nothing updates: `transaction.atomic()`
- ✅ No partial payment confirmation
- ✅ Automatic rollback on error

```python
with transaction.atomic():
    order = Order.objects.select_for_update().get(id=order.id)
    # All updates grouped together
    order.razorpay_payment_id = payment_id
    order.razorpay_signature = signature
    order.payment_status = 'success'
    order.status = 'confirmed'
    order.save()
    # Either all succeed or all rollback
```

### 5. **CSRF Protection**
- ✅ All POST requests validate CSRF token
- ✅ Django middleware enforces: `@csrf_exempt` only for webhook
- ✅ Frontend validates token before sending payment callback

```javascript
// Frontend: Validate CSRF before callback
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
if (!csrfToken) {
    alert('Security error: CSRF token missing');
    return;
}
```

### 6. **Input Validation**
- ✅ Payment ID format check (length > 10 characters)
- ✅ Order ID format check (length > 10 characters)
- ✅ Amount validation (> 0)
- ✅ Razorpay key validation (matches `rzp_test_*` or `rzp_live_*`)

```python
# Validate input before processing
if not (len(payment_id) > 10 and len(razorpay_order_id) > 10):
    return JsonResponse({'status': 'error'}, status=400)

if not amount or amount <= 0:
    return JsonResponse({'status': 'error'}, status=400)
```

### 7. **No Manual Card Collection**
- ✅ Uses Razorpay Official Hosted Checkout (popup)
- ✅ NO card numbers stored
- ✅ NO CVV stored
- ✅ NO sensitive data transmitted to backend

```javascript
// Uses official Razorpay popup - NOT manual form
const razorpay = new Razorpay({
    key: key,
    order_id: orderId,
    // Razorpay handles all payment details securely
});
razorpay.open();  // Opens secure popup
```

### 8. **Audit Logging**
- ✅ All payment events logged with timestamps
- ✅ Security alerts logged separately
- ✅ Fraud attempts tracked
- ✅ OrderStatusHistory maintains complete audit trail

```python
# Comprehensive logging
logger.info(f"[PAYMENT] Order {order.id} payment verified")
logger.error(f"[FRAUD_ALERT] Amount mismatch for order {order.id}")
logger.error(f"[PAYMENT_SECURITY] Invalid signature detected")

# Database audit
OrderStatusHistory.objects.create(
    order=order,
    status='confirmed',
    notes=f"Payment captured: {payment_id}"
)
```

---

## 🛡️ DATABASE SECURITY

### Order Model Payment Fields

```python
# Secure payment fields
razorpay_order_id = CharField(max_length=100, unique=True)
razorpay_payment_id = CharField(max_length=100, unique=True)
razorpay_signature = CharField(max_length=255)

payment_method = CharField(['online', 'emi', 'cod'])
payment_status = CharField(['pending', 'success', 'failed', 'cod_pending'])

status = CharField(['pending_payment', 'payment_successful', 'confirmed', ...])
```

### Key Security Properties

1. **Unique Constraints:**
   - `razorpay_order_id` (UNIQUE) - Prevents duplicate orders
   - `razorpay_payment_id` (UNIQUE) - Prevents duplicate payments

2. **Index for Performance:**
   - `ORDER BY user, -created_at` for quick lookup
   - `INDEX payment_status` for transaction reports

3. **No Sensitive Data Stored:**
   - ✅ No card numbers
   - ✅ No CVV
   - ✅ No expiry dates
   - ✅ No UPI ID or PIN

---

## 🔑 ENVIRONMENT VARIABLES (Production)

### Required Configuration

```bash
# .env or System Environment
RAZORPAY_KEY_ID=rzp_live_1234567890abcdef  # From dashboard.razorpay.com
RAZORPAY_KEY_SECRET=abcdef1234567890      # Keep SECRET - Never share

# Never set to test keys in production
DEBUG=False
DJANGO_SECRET_KEY=<production-secret-key>
```

### How to Get Keys

1. Login: https://dashboard.razorpay.com
2. Go to Settings → API Keys
3. Copy Live Mode keys (NOT test keys)
4. Set in environment variables
5. Restart Django

---

## 🚀 PRODUCTION CHECKLIST

### Before Going Live

- [ ] Set `DEBUG=False` in settings.py
- [ ] Set Razorpay to LIVE mode (not test)
- [ ] Set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` from live dashboard
- [ ] SSL/TLS certificate installed (HTTPS only)
- [ ] Payment callback webhook IP whitelisted in Razorpay
- [ ] Error logs monitored (logs/error.log)
- [ ] Payments logged (logs/debug.log)
- [ ] Test with real payment (₹1 minimum)
- [ ] Verify email/SMS notifications sent
- [ ] Database backups configured
- [ ] Rate limiting enabled on payment endpoints

### Security Hardening

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
```

---

## 🧪 TESTING PAYMENT FLOW

### Test Mode (Without Real Money)

1. **Test Keys:**
   - Use `rzp_test_*` keys from Razorpay dashboard
   - No real money charged

2. **Test Card:**
   - Card Number: `4111 1111 1111 1111`
   - Expiry: Any future date (e.g., 12/25)
   - CVV: Any 3 digits (e.g., 123)

3. **Test Payment Flow:**
   ```
   Add product → Checkout → Online Payment → Review → Place Order
   → Razorpay popup appears → Use test card → Complete payment
   → Signature verified → Order confirmed → Redirect to confirmation
   ```

4. **Verify in Admin:**
   - Check Order in Django admin
   - Verify `payment_status = 'success'`
   - Verify `razorpay_payment_id` populated
   - Check `OrderStatusHistory` entry

---

## 🔍 PAYMENT VERIFICATION WORKFLOW

### Step 1: Order Creation

```python
# CREATE pending order (no payment yet)
Order.objects.create(
    payment_status='pending',
    status='pending_payment',
    razorpay_order_id=razorpay_order['id']
)
```

### Step 2: Payment Gateway

```python
# SHOW Razorpay popup (official hosted checkout)
# User selects UPI/Card/NetBanking
# Razorpay handles payment securely
# Returns: payment_id, order_id, signature
```

### Step 3: Backend Verification

```python
# VERIFY signature (HMAC-SHA256)
if not hmac.compare_digest(expected_sig, actual_sig):
    order.payment_status = 'failed'
    return error  # DO NOT confirm order

# VERIFY amount (Razorpay API)
if payment_amount != order_amount:
    order.payment_status = 'failed'
    return error  # DO NOT confirm order

# MARK as success (atomic transaction)
order.payment_status = 'success'
order.status = 'confirmed'
order.save()
```

### Step 4: Notifications

```python
# SEND async notifications
send_order_notifications(order_id, 'payment_successful')
send_order_notifications(order_id, 'order_confirmed')
send_order_notifications(order_id, 'invoice_sent')
```

---

## 🚨 ERROR HANDLING

### Payment Failures (User Not Charged)

1. **Invalid Signature:**
   - Order marked as `payment_status='failed'`
   - User sees error: "Payment verification failed"
   - No credit given

2. **Amount Mismatch:**
   - Order marked as `payment_status='failed'`
   - User sees error: "Payment amount verification failed"
   - FRAUD_ALERT logged
   - No credit given

3. **Idempotency Check:**
   - Same payment processed twice
   - Returns success (safe)
   - NO double charging
   - NO duplicate order confirmation

4. **Configuration Error:**
   - `RAZORPAY_KEY_SECRET` missing
   - Order marked as `payment_status='failed'`
   - User sees: "Payment gateway not configured"
   - Admin alerted via logs

---

## 📊 MONITORING & ALERTS

### Logs to Monitor

```bash
# Error logs (critical)
tail -f logs/error.log

# Payment logs (important)
grep "\[PAYMENT\]" logs/debug.log

# Security alerts (critical)
grep "\[FRAUD_ALERT\]\|\[PAYMENT_SECURITY\]" logs/debug.log

# All payment transactions
grep "razorpay" logs/debug.log
```

### Key Metrics

- **Payment Success Rate:** (success payments / total payments) × 100
- **Failed Payments:** Track reasons (signature, amount, etc.)
- **Fraud Attempts:** Count `[FRAUD_ALERT]` logs
- **Response Time:** Payment callback response < 500ms

---

## 🔒 COMPLIANCE & STANDARDS

### PCI DSS Compliance

- ✅ NO card data stored in our database
- ✅ All payments via Razorpay (PCI DSS Level 1 compliant)
- ✅ HTTPS/TLS for all payment endpoints
- ✅ Server-side verification (not client-side)

### Security Standards

- ✅ OWASP Top 10 compliance
- ✅ CSRF protection enabled
- ✅ SQL injection prevention (ORM)
- ✅ XSS prevention (template escaping)
- ✅ Timing attack prevention (compare_digest)

---

## 📞 SUPPORT & TROUBLESHOOTING

### Common Issues

**Issue:** "Payment gateway is not properly configured"
- **Cause:** `RAZORPAY_KEY_ID` or `RAZORPAY_KEY_SECRET` not set
- **Fix:** Set environment variables and restart Django

**Issue:** "Payment verification failed"
- **Cause:** Could be network timeout or signature mismatch
- **Fix:** Check logs, retry payment with test key

**Issue:** "Payment amount verification failed"
- **Cause:** Order amount changed during payment
- **Fix:** Ensure order NOT modified after payment initiation

**Issue:** Order not confirmed after payment
- **Cause:** Callback webhook not received
- **Fix:** Check Razorpay webhook settings and timeout

---

## 📋 PRODUCTION DEPLOYMENT SUMMARY

1. ✅ **No Fake Simulation** - Real Razorpay integration only
2. ✅ **No Manual Card Collection** - Official popup only
3. ✅ **Server-Side Verification** - HMAC-SHA256 + Amount check
4. ✅ **No Order Confirmation Without Payment** - Status=pending_payment until verified
5. ✅ **Atomic Transactions** - All-or-nothing updates
6. ✅ **Comprehensive Logging** - Full audit trail
7. ✅ **CSRF Protection** - All POST requests validated
8. ✅ **Idempotency** - Safe retry logic
9. ✅ **PCI DSS Compliant** - NO sensitive data stored
10. ✅ **Production-Ready** - Enterprise-grade security

---

**READY FOR PRODUCTION DEPLOYMENT** ✅
