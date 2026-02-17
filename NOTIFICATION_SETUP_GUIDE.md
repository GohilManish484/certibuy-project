# Notification System Setup Guide

## Problem
Notifications (email and SMS) are not being sent because:
1. Redis server is not running (required for Celery)
2. Celery worker is not running (processes notification tasks)
3. Environment variables not configured (.env file missing)

## Quick Setup (3 Steps)

### Step 1: Install and Start Redis

**Option A: Using Windows Installer (Recommended)**
1. Download Redis for Windows: https://github.com/microsoftarchive/redis/releases
2. Download `Redis-x64-3.2.100.msi`
3. Install with default settings
4. Redis will auto-start as a Windows service

**Option B: Using WSL2**
```bash
wsl --install
wsl
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**Option C: Using Docker**
```powershell
docker run -d -p 6379:6379 redis:latest
```

**Verify Redis is running:**
```powershell
python -c "import redis; r = redis.Redis(); r.ping(); print('Redis OK')"
```

### Step 2: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` and add your credentials:

**Email (Gmail):**
- Go to Google Account → Security → 2-Step Verification → App Passwords
- Generate app password for "Mail"
- Add to `.env`:
  ```
  EMAIL_HOST_USER=your-email@gmail.com
  EMAIL_HOST_PASSWORD=your-16-digit-app-password
  ```

**SMS (MSG91):**
- Sign up at https://msg91.com
- Get API key from Dashboard
- Add to `.env`:
  ```
  MSG91_API_KEY=your-api-key-here
  ```

**SMS (Fast2SMS - Alternative):**
- Sign up at https://www.fast2sms.com
- Get API key from Dashboard
- Add to `.env`:
  ```
  FAST2SMS_API_KEY=your-api-key-here
  SMS_PROVIDER=fast2sms
  ```

### Step 3: Start Celery Worker

Open a **new terminal** and run:
```powershell
celery -A certibuy worker --loglevel=info --pool=solo
```

Keep this terminal running. You should see:
```
[tasks]
  . orders.tasks.send_order_email
  . orders.tasks.send_order_notifications
  . orders.tasks.send_order_sms

celery@hostname ready.
```

## Testing Notifications

### Test Email (Without Order)
```python
python manage.py shell
```
```python
from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test message.',
    'noreply@certibuy.com',
    ['customer@email.com'],
    fail_silently=False,
)
# Should print: 1
```

### Test SMS (Without Order)
```python
from orders.services.sms_service import send_sms
result = send_sms('+919876543210', 'Test message from CERTIBUY')
print(result)  # Should print: True
```

### Test Full Order Notification
1. Place a test order through the website
2. Complete payment
3. Check Celery terminal - you should see:
   ```
   [2026-02-16 10:30:00] Task orders.tasks.send_order_notifications[xxx] received
   [2026-02-16 10:30:01] Sending payment_successful email to customer@email.com
   [2026-02-16 10:30:02] Sending payment_successful SMS to +919876543210
   ```
4. Customer should receive 3 emails and 3 SMS:
   - Payment successful
   - Order confirmed
   - Invoice sent (with download link)

## Troubleshooting

### No emails received
- Check spam/junk folder
- Verify Gmail app password is correct (16 digits, no spaces)
- Check Celery terminal for errors
- View Django logs: `python manage.py runserver` (check terminal output)

### No SMS received
- Check SMS provider credits/balance
- Verify phone number format: +91XXXXXXXXXX (with country code)
- Check Celery terminal for SMS errors
- Try switching providers in `.env`: `SMS_PROVIDER=fast2sms`

### Redis connection refused
- Ensure Redis is running: `redis-cli ping` (should return "PONG")
- Windows: Check Services → Redis is "Running"
- WSL: `sudo service redis-server status`
- Docker: `docker ps` (should show redis container)

### Celery worker not starting
- Ensure Redis is running first
- Windows requires `--pool=solo` flag
- Check for port conflicts on 6379

## Running in Production

### Using Supervisor (Linux)
```ini
[program:certibuy-celery]
command=/path/to/venv/bin/celery -A certibuy worker --loglevel=info
directory=/path/to/certibuy
user=www-data
autostart=true
autorestart=true
```

### Using Windows Service (NSSM)
```powershell
nssm install CertiBuyCelery "C:\cirtibuy\.venv\Scripts\celery.exe" "-A certibuy worker --loglevel=info --pool=solo"
nssm set CertiBuyCelery AppDirectory "C:\cirtibuy"
nssm start CertiBuyCelery
```

## Notification Events

The system sends notifications for 7 events:

1. **payment_successful** - When payment is verified
2. **order_confirmed** - When order is created
3. **invoice_sent** - Invoice ready with download link
4. **order_shipped** - When seller marks as shipped
5. **out_for_delivery** - When in transit
6. **order_delivered** - When delivered
7. **refund_processed** - When refund is issued

Each event triggers both email (HTML template) and SMS (text message).

## Alternative: Send Notifications Synchronously (Quick Fix)

If you can't set up Redis/Celery immediately, you can send notifications synchronously (blocks request until sent):

**Edit `orders/views.py` line 449:**
```python
# Change from:
send_order_notifications.delay(order.id, 'payment_successful')

# To:
send_order_notifications(order.id, 'payment_successful')
```

⚠️ **Warning**: This will slow down the payment callback (2-3 seconds per order). Use only for testing.

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| EMAIL_HOST_USER | Yes | - | SMTP username/email |
| EMAIL_HOST_PASSWORD | Yes | - | SMTP password/app password |
| MSG91_API_KEY | Yes* | - | MSG91 API key |
| FAST2SMS_API_KEY | Yes* | - | Fast2SMS API key |
| CELERY_BROKER_URL | Yes | redis://localhost:6379/0 | Redis URL |
| SMS_PROVIDER | No | msg91 | 'msg91' or 'fast2sms' |

*At least one SMS provider required

## Next Steps

1. ✅ Install Redis
2. ✅ Create `.env` file with credentials  
3. ✅ Start Celery worker
4. ✅ Place test order
5. ✅ Verify notifications received

## Support

For issues:
- Check Celery terminal for error messages
- Run `python manage.py check` for Django issues
- View notification logs: Admin → Notification Logs
- Test individual components (email, SMS, Redis) separately
