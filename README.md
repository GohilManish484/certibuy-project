# CertiBuy - Enterprise Marketplace Platform

[![Django Version](https://img.shields.io/badge/Django-6.0.2-green.svg)](https://www.djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.12.3-blue.svg)](https://www.python.org/)
[![RBAC](https://img.shields.io/badge/Security-RBAC%20Enabled-red.svg)](https://en.wikipedia.org/wiki/Role-based_access_control)

A secure, enterprise-level marketplace platform for buying and selling certified products with comprehensive Role-Based Access Control (RBAC) and premium Cashify-style product pages.

---

## 🎉 Latest Update: Cashify-Style Product Experience (December 2024)

✅ **Complete professional refurbished marketplace redesign implemented!**

### New Premium Features
- 🖼️ Vertical thumbnail gallery with click-to-switch
- 🎨 Interactive condition selector with dynamic pricing
- 💾 Storage selector (64GB/128GB/256GB) with add-on pricing
- 🌈 Color selector with visual swatches
- 📦 Delivery pincode check with estimate
- 💳 Payment methods display (EMI, UPI, Card, COD)
- 🎁 Combo offers section
- 📌 Sticky buy bar on scroll
- 📋 Product details tabs
- ⭐ Rating and review display
- ✅ Trust badges (warranty, returns, certified)

### Quick Links to Documentation
- 📖 [Quick Reference Guide](CASHIFY_QUICK_REFERENCE.md) - Developer & user guide
- 📚 [Full Implementation Doc](CASHIFY_STYLE_IMPLEMENTATION.md) - Complete feature details
- 🎨 [Visual Guide](CASHIFY_VISUAL_GUIDE.md) - Layout diagrams & design specs
- 📊 [Implementation Summary](CASHIFY_REDESIGN_SUMMARY.md) - Project completion report
- 🔐 [RBAC Guide](RBAC_IMPLEMENTATION_GUIDE.md) - Security & access control
- ✅ [Completion Report](COMPLETION_REPORT.md) - Overall system status

---

## 🚀 Quick Start

### 1. Installation Commands
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Database Configuration (MySQL)
```powershell
$env:MYSQL_DATABASE = "certibuy"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = ""
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:DJANGO_SECRET_KEY = "change-me-in-production"
```

## Initial Setup Commands
```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 🔐 RBAC Features

### User Roles
- **Customer** - Browse and purchase certified products
- **Seller** - Submit products for certification  
- **Inspector** - Review and certify products
- **Admin** - Full system management

### Security Features
- ✅ Login attempt throttling (IP-based)
- ✅ Separate admin authentication portal
- ✅ Multi-layer access control (Middleware + Decorators)
- ✅ Role-based navigation and dashboards
- ✅ Secure logout (POST with CSRF protection)
- ✅ Custom 403 error pages

### Quick Test Users Setup
```bash
python manage.py shell -c "
from accounts.models import User
User.objects.create_user(username='customer1', email='customer@test.com', password='Test123!', role='customer')
User.objects.create_user(username='seller1', email='seller@test.com', password='Test123!', role='seller')
User.objects.create_user(username='inspector1', email='inspector@test.com', password='Test123!', role='inspector')
User.objects.create_superuser(username='admin1', email='admin@test.com', password='Admin123!')
print('✅ Test users created!')
"
```

### Dashboard URLs
- Customer: `http://127.0.0.1:8000/customer/dashboard/`
- Seller: `http://127.0.0.1:8000/seller/dashboard/`
- Inspector: `http://127.0.0.1:8000/inspector/dashboard/`
- Admin: `http://127.0.0.1:8000/admin-dashboard/`

---

## 📖 Documentation

### For Developers
- [RBAC Implementation Guide](RBAC_IMPLEMENTATION_GUIDE.md) - Complete testing guide
- [Quick Reference](QUICK_REFERENCE.md) - Fast commands and scenarios
- [Architecture Diagrams](ARCHITECTURE_DIAGRAM.md) - System architecture
- [Completion Report](COMPLETION_REPORT.md) - Implementation summary

### For Testing
See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for:
- Test user creation
- Login scenarios
- Access control verification
- Dashboard functionality

---

## Folder Structure
```
certibuy/
├─ accounts/                    # User authentication & RBAC
│  ├─ decorators.py            # ✨ NEW: Role-based decorators
│  ├─ middleware.py            # ✨ NEW: RBAC middleware
│  └─ views.py                 # Enhanced with throttling
├─ certibuy/                   # Project settings
│  ├─ settings.py              # Updated: Middleware + cache
│  └─ urls.py
├─ core/                       # Core functionality
│  └─ views.py                 # Added 4 dashboard views
├─ sellers/                    # Seller product submissions
├─ inspections/                # Product inspections
├─ products/                   # Product catalog
├─ orders/                     # Order management
├─ templates/
│  ├─ dashboards/              # ✨ NEW: Role-specific dashboards
│  │  ├─ customer_dashboard.html
│  │  ├─ seller_dashboard.html
│  │  ├─ inspector_dashboard.html
│  │  └─ admin_dashboard.html
│  ├─ errors/                  # ✨ NEW: Error pages
│  │  └─ 403.html
│  ├─ accounts/
│  │  └─ admin_login.html      # ✨ NEW: Secure admin login
│  ├─ base.html                # Updated: Role-based navigation
│  └─ pages/
│     └─ home.html             # Updated: Role-based CTAs
├─ media/                      # User uploads
├─ static/                     # Static assets
├─ manage.py
├─ requirements.txt
├─ QUICK_REFERENCE.md          # ✨ NEW: Fast testing guide
├─ RBAC_IMPLEMENTATION_GUIDE.md # ✨ NEW: Complete guide
├─ ARCHITECTURE_DIAGRAM.md     # ✨ NEW: System architecture
└─ COMPLETION_REPORT.md        # ✨ NEW: Implementation report
```

---

## 🎯 Key Features

### Security
- Enterprise-level Role-Based Access Control
- Login attempt throttling (5 attempts per IP)
- Separate authentication portals (public + admin)
- Multi-layer security (middleware + decorators)
- CSRF protection on all forms
- Secure logout (POST-only)

### User Experience
- Role-specific dashboards with statistics
- Dynamic navigation based on user role
- Professional 403 error pages
- Responsive design
- Real-time submission/inspection counts

### Business Features
- Product submission workflow
- Inspection process management
- Order processing (upcoming)
- Shopping cart functionality
- User profile management

---

## 🧪 Testing

### Quick Verification (2 minutes)
```bash
# 1. Create test users
python manage.py shell -c "..." # See command above

# 2. Start server
python manage.py runserver

# 3. Test login
# Visit: http://127.0.0.1:8000/accounts/login/
# Login: customer@test.com / Test123!
# Expected: Redirect to customer dashboard ✅

# 4. Test access control
# Visit: http://127.0.0.1:8000/seller/dashboard/
# Expected: 403 Forbidden page ✅
```

For comprehensive testing, see [QUICK_REFERENCE.md](QUICK_REFERENCE.md).

---

## 🔧 Configuration

### Current Setup (Development)
- `DEBUG = True`
- `ALLOWED_HOSTS = ['*']`
- LocMemCache for login throttling
- SQLite database

### Production Recommendations
```python
# In settings.py:
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Use Redis for cache:
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

## 📊 System Status

- ✅ Django System Check: 0 errors
- ✅ All migrations applied
- ✅ RBAC fully implemented
- ✅ All dashboards functional
- ✅ Documentation complete
- ⏳ Manual testing required

---

## 💡 Key Commands

```bash
# Create test users
python manage.py shell -c "..." # See Quick Start section

# Start development server
python manage.py runserver

# Clear login throttling cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Run Django checks
python manage.py check

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

---

## 📞 Support

For questions or issues:
1. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common tasks
2. Review [RBAC_IMPLEMENTATION_GUIDE.md](RBAC_IMPLEMENTATION_GUIDE.md) for detailed instructions
3. See [COMPLETION_REPORT.md](COMPLETION_REPORT.md) for troubleshooting tips

---

## 🏆 What's New

### Version 2.0 (Latest) - Enterprise RBAC
- ✨ Complete RBAC implementation
- ✨ 4 role-specific dashboards
- ✨ Login throttling system
- ✨ Separate admin authentication
- ✨ Custom error pages
- ✨ Comprehensive documentation

### Version 1.0 - Core Features
- User authentication
- Product catalog
- Shopping cart
- Order management
- Basic role system

---

## 🎉 Ready to Test!

Everything is set up and ready for testing. Follow the Quick Start guide above to create test users and verify the RBAC system.

**Happy Testing! 🚀**

---

**Project Status:** ✅ Production Ready (after testing)  
**Django Version:** 6.0.2  
**Python Version:** 3.12.3  
**Last Updated:** 2024

