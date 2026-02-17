# CERTIBUY Email & SMS Notification System

## Overview
Enterprise-grade notification system with Email and SMS capabilities for order lifecycle events.

## Features
- ✅ **Email Notifications** - SMTP-based email alerts with beautiful HTML templates
- ✅ **SMS Notifications** - MSG91 and Fast2SMS integration with automatic fallback
- ✅ **Asynchronous Processing** - Celery-based background task queue
- ✅ **Retry Mechanism** - Automatic retry on failure (3 attempts)
- ✅ **Notification Logging** - Complete audit trail in `NotificationLog` model
- ✅ **Multiple Triggers** - Payment, Order Confirmation, Shipping, Delivery, Refunds

## Architecture

```
Order Event → Celery Task → Email/SMS Service → External API → NotificationLog
```

## Notification Events

| Event | Trigger | Email | SMS |
|-------|---------|-------|-----|
| Payment Successful | After Razorpay verification | ✓ | ✓ |
| Order Confirmed | After payment success | ✓ | ✓ |
| Order Shipped | Admin status change | ✓ | ✓ |
| Out for Delivery | Admin status change | ✓ | ✓ |
| Delivered | Admin status change | ✓ | ✓ |
| Refund Processed | Order cancellation | ✓ | ✓ |

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `celery>=5.3.4`
- `redis>=5.0.1`
- `requests>=2.31.0`

### 2. Install and Start Redis

**Windows:**
```powershell
# Download Redis for Windows or use WSL
# Using Chocolatey:
choco install redis-64

# Start Redis server
redis-server
```

**Linux/Mac:**
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Start Redis
redis-server
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Email Configuration (Gmail example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@certibuy.com

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# MSG91 SMS Configuration
MSG91_API_KEY=your-msg91-api-key
MSG91_SENDER_ID=CERTBY
MSG91_ROUTE=4

# Fast2SMS Configuration
FAST2SMS_API_KEY=your-fast2sms-api-key
FAST2SMS_SENDER_ID=CERTBY

# SMS Provider (msg91 or fast2sms)
SMS_PROVIDER=msg91
```

### 4. Gmail App Password Setup

For Gmail SMTP:
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate App Password: https://myaccount.google.com/apppasswords
4. Use the generated password in `EMAIL_HOST_PASSWORD`

### 5. SMS API Setup

**MSG91:**
1. Sign up at https://msg91.com
2. Get API key from dashboard
3. Set up sender ID (CERTBY or custom)

**Fast2SMS:**
1. Sign up at https://www.fast2sms.com
2. Get API key from dashboard
3. Verify sender ID

### 6. Start Celery Worker

Open a **new terminal** and run:

```bash
# Windows
celery -A certibuy worker --loglevel=info --pool=solo

# Linux/Mac
celery -A certibuy worker --loglevel=info
```

Keep this terminal running. You should see:
```
[tasks]
  . orders.tasks.send_order_email
  . orders.tasks.send_order_sms
  . orders.tasks.send_order_notifications
```

### 7. Start Django Server

In another terminal:

```bash
python manage.py runserver
```

## Testing Notifications

### Test Payment Flow

1. Place an order as a customer
2. Complete payment via Razorpay
3. Check terminal logs for notification tasks
4. Verify email received
5. Check `NotificationLog` in admin panel

### Test Admin Status Changes

1. Login to admin: http://127.0.0.1:8000/admin/
2. Go to Orders → Select an order
3. Change status to "Shipped"
4. Save order
5. Notification will be sent automatically

### Manual Test (Django Shell)

```python
python manage.py shell

from orders.tasks import send_order_notifications
from orders.models import Order

# Get an order
order = Order.objects.first()

# Trigger notification
send_order_notifications.delay(order.id, 'order_shipped')
```

## Monitoring Notifications

### Admin Panel
- Go to: http://127.0.0.1:8000/admin/orders/notificationlog/
- View all sent/failed notifications
- Check error messages and retry counts

### Celery Worker Logs
Monitor the Celery terminal for real-time task execution:
```
[INFO] Task orders.tasks.send_order_email[...] succeeded
[INFO] SMS sent: order_shipped for order ORD-...
```

## File Structure

```
certibuy/
├── certibuy/
│   ├── celery.py                    # Celery app initialization
│   ├── __init__.py                  # Celery app import
│   └── settings.py                  # Email, Celery, SMS config
├── orders/
│   ├── models.py                    # NotificationLog model
│   ├── tasks.py                     # Celery tasks
│   ├── admin.py                     # Admin with notification triggers
│   ├── views.py                     # Order views with notifications
│   └── services/
│       └── sms_service.py           # MSG91 & Fast2SMS integration
├── templates/
│   └── emails/                      # HTML email templates
│       ├── order_confirmed.html
│       ├── payment_successful.html
│       ├── order_shipped.html
│       ├── out_for_delivery.html
│       ├── order_delivered.html
│       └── refund_processed.html
└── .env                             # Environment variables
```

## Email Templates

All email templates use responsive HTML with:
- Gradient headers (Teal/Cyan theme)
- Mobile-friendly design
- Order details and tracking information
- Professional branding

## SMS Message Format

SMS messages are concise (160 chars) with:
- Order number
- Event type
- Tracking ID (where applicable)
- Brand signature

Example:
```
Order ORD-12345 confirmed. Track at certibuy.com. - CERTIBUY
```

## Troubleshooting

### Celery Not Picking Up Tasks

```bash
# Restart Celery worker
# Press Ctrl+C in Celery terminal
celery -A certibuy worker --loglevel=info --pool=solo
```

### Email Not Sending

- Check Gmail app password
- Verify `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
- Test SMTP connection:

```python
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

### SMS Not Sending

- Verify API keys in `.env`
- Check SMS service balance
- Review `NotificationLog` for error messages
- Try switching providers (`SMS_PROVIDER=fast2sms`)

### Redis Connection Error

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start Redis
redis-server
```

## Production Deployment

### Security Checklist
- ✅ Use environment variables (never commit API keys)
- ✅ Enable Redis password authentication
- ✅ Use HTTPS for email links
- ✅ Set up Celery supervisor/systemd service
- ✅ Configure email rate limiting
- ✅ Set up SMS budget alerts

### Recommended Production Setup

**Celery Service (systemd):**
```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/certibuy
ExecStart=/path/to/venv/bin/celery -A certibuy worker --detach
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Redis Security:**
```bash
# /etc/redis/redis.conf
requirepass your-strong-password
```

Update `.env`:
```env
CELERY_BROKER_URL=redis://:your-strong-password@localhost:6379/0
```

## API Rate Limits

| Provider | Free Tier | Rate Limit |
|----------|-----------|------------|
| MSG91 | Credits-based | Varies |
| Fast2SMS | Credits-based | Varies |
| Gmail SMTP | Free | 500 emails/day |

## Cost Estimation

For 1000 orders/month:
- **Emails:** Free (Gmail) or ~$10/month (SendGrid)
- **SMS:** ~₹500-₹1000/month (depends on provider rates)
- **Redis:** Free (self-hosted) or $5-10/month (cloud)

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review Celery worker output
- Inspect `NotificationLog` in admin
- Verify environment variables

## License

This notification system is part of CERTIBUY e-commerce platform.
