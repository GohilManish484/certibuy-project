# NOTIFICATION SYSTEM - QUICK FIX GUIDE

## Current Status

✅ **SMS WORKING** - Invoice and notifications are being sent via SMS!  
❌ **EMAIL NOT WORKING** - Gmail credentials need to be corrected

## Fix Email in 3 Steps

### Step 1: Generate Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click "Security" in left menu
3. Enable "2-Step Verification" if not already enabled
4. Go back to Security → search for "App passwords"
5. Select app: "Mail", device: "Windows Computer"
6. Click "Generate"
7. **Copy the 16-digit password** (e.g., `abcd efgh ijkl mnop`)

### Step 2: Update .env File

Open `.env` file and update these lines:

```env
EMAIL_HOST_USER=your-actual-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-digit-app-password-here
DEFAULT_FROM_EMAIL=your-actual-email@gmail.com
```

**Important**: 
- Remove spaces from the app password
- Use your real Gmail address
- Save the file

### Step 3: Test

Run this command:

```powershell
python test_single_notification.py
```

You should see:
- ✓ Email sent successfully
- ✓ SMS sent successfully

## What's Working Now (Without Email Fix)

Even with the email issue, these are working:

1. ✅ **SMS notifications sent** to customer phone numbers
2. ✅ **Invoice SMS** with download link
3. ✅ **Order confirmation SMS**
4. ✅ **Payment successful SMS**
5. ✅ **Notification logs** saved in database

## Email Won't Work Until You:

1. Use a valid Gmail address in `.env`
2. Generate and use an App Password (not your regular Gmail password)
3. Make sure 2-Step Verification is enabled on your Google account

## Alternative: Skip Email for Now

If you don't want to set up email right now, SMS alone will work for:
- Order confirmations
- Invoice delivery
- Payment confirmations
- Shipping updates

**To disable email notifications** (optional), edit `.env`:

```env
# Temporarily disable email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

This will print emails to console instead of sending them.

## Verifying Everything Works

After fixing email, place a test order and check:

1. **Customer receives 3 SMS**:
   - Payment successful
   - Order confirmed  
   - Invoice sent (with download link)

2. **Customer receives 3 emails**:
   - Payment successful
   - Order confirmed
   - Invoice ready

3. **Admin can view logs**:
   - Go to Django Admin → Notification Logs
   - See all sent notifications

## Production Checklist

For production deployment:

- [ ] Set up Gmail App Password
- [ ] Update `.env` with real credentials
- [ ] Test with real order
- [ ] Install Redis (optional, for better performance)
- [ ] Start Celery worker (optional, for async sending)
- [ ] Monitor notification logs for failures

## Current Configuration

**Notification Mode**: Synchronous (CELERY_TASK_ALWAYS_EAGER=True)
**SMS Provider**: MSG91
**Email Provider**: Gmail SMTP
**Fallback**: SMS will always work, email optional

## Need Help?

**Email Error**: "Username and Password not accepted"  
**Solution**: Use Gmail App Password, not regular password

**SMS Not Received**: Check SMS balance and phone number format (+91XXXXXXXXXX)

**Neither Working**: Check `.env` file has correct credentials

---

**Last Update**: 2026-02-16  
**Status**: SMS Working ✅, Email Needs Configuration ❌
