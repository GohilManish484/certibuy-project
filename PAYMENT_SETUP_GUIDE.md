# Payment System Setup Guide

## Issues Fixed

✅ **Enhanced Payment Gateway** - Improved error handling and CSRF token validation  
✅ **Better User Feedback** - Button states and loading indicators  
✅ **Debugging Tools** - Added diagnostic script to identify payment issues  

## Common Payment Issues & Solutions

### Issue 1: Razorpay Credentials Not Set
**Symptoms:** "Payment gateway is not properly configured" or blank payment form

**Solution:**
1. Get your Razorpay API keys from: https://dashboard.razorpay.com/app/dashboard
2. Set environment variables:
   ```bash
   set RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
   set RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxx
   ```
3. Restart the Django server

### Issue 2: Payment Button Not Opening
**Symptoms:** Click "Complete Payment" but nothing happens

**Solution:**
1. Check browser console for errors (F12 > Console tab)
2. Verify Razorpay JavaScript library is loading:
   - Should see `checkout.razorpay.com` in Network tab
3. Clear browser cache and try again
4. Disable browser extensions that block scripts

### Issue 3: "Payment Verification Failed"
**Symptoms:** Payment completes but shows verification error

**Solution:**
1. Run diagnostic test:
   ```bash
   python manage.py shell < test_payment_system.py
   ```
2. Check that RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET match exactly
3. Verify signature validation in Django logs
4. Check CSRF token is present in the form

### Issue 4: EMI Payment Not Working
**Symptoms:** EMI option appears but payment fails

**Solution:**
1. EMI requires additional Razorpay configuration
2. Contact Razorpay support to enable EMI on your account
3. Test with online payment first to ensure basic payment works
4. Some EMI options may not be available for test mode

### Issue 5: Payment Success But Order Not Created
**Symptoms:** Payment goes through but no order confirmation

**Solution:**
1. Check Django logs for errors:
   ```bash
   tail -f logs/error.log
   ```
2. Verify database connection:
   ```bash
   python manage.py dbshell
   SELECT COUNT(*) FROM orders_order;
   ```
3. Check if order exists in admin panel
4. Verify payment callback is being called

## Testing the Payment System

### Quick Test (Development Only)
1. Use test Razorpay credentials
2. Test card: 4111 1111 1111 1111
3. Any future date expiry
4. Any CVV (e.g., 123)

### Run Diagnostic Script
```bash
python manage.py shell
>>> exec(open('test_payment_system.py').read())
```

### Check Payment Logs
```bash
# View payment-related logs
grep -i "payment\|razorpay" logs/debug.log | tail -50

# View all errors
grep -i "error" logs/error.log | tail -20
```

## Configuration Checklist

- [ ] RAZORPAY_KEY_ID environment variable set
- [ ] RAZORPAY_KEY_SECRET environment variable set  
- [ ] Razorpay SDK installed: `pip install razorpay>=1.4.2`
- [ ] Payment callback URL registered (if needed)
- [ ] CSRF middleware enabled
- [ ] Database migrations run: `python manage.py migrate`
- [ ] Static files collected: `python manage.py collectstatic`

## Payment Flow Diagram

```
1. User at Checkout Step 2
   ↓ Selects payment method (Online/EMI/COD)
   ↓
2. Checkout Step 3 (Review)
   ↓ Submits order
   ↓
3. Backend Creates Order
   ↓ Creates Razorpay Order (if online/EMI)
   ↓
4. Redirects to Payment Gateway
   ↓ Shows encrypted payment form
   ↓
5. User Completes Payment
   ↓ Razorpay processes payment
   ↓
6. Payment Callback
   ↓ Backend verifies signature
   ↓ Updates order status
   ↓
7. Order Confirmation
   ↓ Shows success message
```

## Support

For Razorpay-specific issues:
- Email: support@razorpay.com
- Dashboard: https://dashboard.razorpay.com
- Documentation: https://razorpay.com/docs

For application issues:
- Check error logs in `logs/` directory
- Run diagnostic script: `python test_payment_system.py`
- Verify database is accessible
- Check environment variables are set correctly
