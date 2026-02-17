# Security Checklist for Production Deployment

## Pre-Deployment Security Audit

### 1. Environment Configuration
- [ ] SECRET_KEY set via environment variable
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured with actual domain names
- [ ] Database credentials secured (not in settings.py)
- [ ] All sensitive data in environment variables

### 2. HTTPS & SSL
- [ ] SECURE_SSL_REDIRECT=True
- [ ] SESSION_COOKIE_SECURE=True
- [ ] CSRF_COOKIE_SECURE=True
- [ ] SECURE_HSTS_SECONDS=31536000
- [ ] SSL certificate installed and valid

### 3. Security Headers (Automated)
- [x] X-Content-Type-Options: nosniff
- [x] X-Frame-Options: DENY
- [x] X-XSS-Protection: 1; mode=block
- [x] Content-Security-Policy configured
- [x] Referrer-Policy set
- [x] Permissions-Policy configured

### 4. Authentication & Authorization
- [x] Login throttling implemented (5 attempts, 15-min lockout)
- [x] Strong password validation enabled
- [x] Role-based access control enforced
- [x] @login_required on all sensitive views
- [x] Horizontal privilege escalation prevented
- [ ] 2FA enabled for admin accounts (optional, requires external package)

### 5. File Upload Security
- [x] File type validation (JPEG, PNG, WEBP only)
- [x] File size limits (5MB max)
- [x] Secure filename generation
- [x] Path traversal prevention
- [x] Content type validation
- [x] Maximum file count per upload

### 6. Error Handling
- [x] Custom 403, 404, 500 error pages
- [x] Error handlers configured
- [x] Sensitive error messages disabled
- [x] Comprehensive logging enabled
- [x] Try/except blocks in critical views

### 7. Session Security
- [x] SESSION_COOKIE_HTTPONLY=True
- [x] SESSION_COOKIE_SAMESITE='Lax'
- [x] Session timeout configured (1 hour)
- [ ] Session rotation on login (Django default)

### 8. CSRF Protection
- [x] CSRF middleware enabled
- [x] CSRF tokens in all POST forms
- [x] CSRF_COOKIE_HTTPONLY=True
- [x] CSRF_COOKIE_SAMESITE='Lax'

### 9. Database Security
- [ ] Database user with minimal privileges
- [ ] Database passwords strong and unique
- [ ] Database backups automated
- [ ] SQL injection prevention (Django ORM used)

### 10. Logging & Monitoring
- [x] Logging configured for errors and warnings
- [x] Security events logged
- [x] Log rotation configured
- [ ] Log monitoring system in place
- [ ] Alert system for critical errors

### 11. Admin Panel Security
- [x] Admin login separate from public login
- [x] Strong admin password requirements
- [ ] Custom admin URL path (not /admin/)
- [ ] Admin access IP whitelist (optional)
- [ ] Admin activity logging

### 12. Additional Hardening
- [x] File upload size limits
- [x] Directory permissions set
- [ ] Static files served via CDN (production)
- [ ] Media files access control
- [ ] Rate limiting on APIs (if applicable)
- [ ] Dependency security scan

## Post-Deployment
- [ ] Security scan completed
- [ ] Penetration testing performed
- [ ] Monitoring dashboards configured
- [ ] Incident response plan documented
- [ ] Regular security updates scheduled

## Commands to Run Before Production

```bash
# 1. Collect static files
python manage.py collectstatic --noinput

# 2. Run migrations
python manage.py migrate

# 3. Create superuser (if not exists)
python manage.py createsuperuser

# 4. Check for security issues
python manage.py check --deploy

# 5. Test error pages
# Set DEBUG=False temporarily and test /404, /403, /500

# 6. Review logs
tail -f logs/django.log
```

## Environment Variables Required

```env
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=your-database-url
ADMIN_PATH=secure-admin-path
```

## Security Contacts
- Report vulnerabilities to: security@certibuy.com
- Emergency contact: [REDACTED]
