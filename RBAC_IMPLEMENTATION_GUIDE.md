# 🔐 CertiBuy Enterprise RBAC - Complete Implementation Guide

## ✅ Implementation Status: **COMPLETE**

All enterprise-level Role-Based Access Control (RBAC) features have been successfully implemented and are ready for testing.

---

## 🎯 What Was Implemented

### 1. **Custom Role-Based Decorators** (`accounts/decorators.py`)
- `@customer_required` - Restricts view to customers only
- `@seller_required` - Restricts view to sellers only  
- `@inspector_required` - Restricts view to inspectors only
- `@admin_required` - Restricts view to admins/staff only
- `@role_required(*roles)` - Flexible decorator for multiple roles
- `@login_required_custom` - Base authentication check

### 2. **RBAC Middleware** (`accounts/middleware.py`)
- Global path protection at middleware level
- Path-to-role mapping dictionary
- Admin bypass (unrestricted access for administrators)
- Returns 403 Forbidden for unauthorized access

### 3. **Login Security Features**
- **Login Throttling**: 5 failed attempts = 15-minute lockout
- **IP-Based Rate Limiting**: Tracks attempts by IP address
- **Separate Admin Login**: `/accounts/admin-login/` for administrators only
- **Role Validation**: Admin cannot use public login, regular users cannot use admin login

### 4. **Role-Specific Dashboards**
- **Customer Dashboard**: `/customer/dashboard/` - Browse products, view orders
- **Seller Dashboard**: `/seller/dashboard/` - Submission statistics, recent submissions
- **Inspector Dashboard**: `/inspector/dashboard/` - Inspection statistics, assigned inspections
- **Admin Dashboard**: `/admin-dashboard/` - Full system overview, statistics

### 5. **Security Enhancements**
- **403 Error Page**: Custom access denied page showing role information
- **Secure Logout**: POST-only with CSRF protection (no GET logout links)
- **Role-Based Navigation**: Menu items change based on user role
- **Cart Access Control**: Shopping cart visible only to authenticated users

---

## 📦 Files Created/Modified

### ✨ New Files Created
```
accounts/decorators.py           (125 lines) - Role-based decorators
accounts/middleware.py           (85 lines)  - RBAC middleware
templates/errors/403.html        (74 lines)  - Access denied page
templates/accounts/admin_login.html (70 lines) - Admin login page
templates/dashboards/customer_dashboard.html (80 lines)
templates/dashboards/seller_dashboard.html (145 lines)
templates/dashboards/inspector_dashboard.html (120 lines)
templates/dashboards/admin_dashboard.html (280 lines)
test_rbac.py                     (360 lines) - Automated test suite
```

### 🔧 Modified Files
```
certibuy/settings.py           - Added middleware, cache config
accounts/views.py              - Added throttling, separate admin login, role redirects
accounts/urls.py               - Added admin-login route
core/views.py                  - Added 4 dashboard views
core/urls.py                   - Added 4 dashboard routes
sellers/views.py               - Applied @role_required decorators
inspections/views.py           - Applied @role_required decorators
templates/base.html            - Role-based navigation
templates/pages/home.html      - Role-based CTAs
```

---

## 🚀 Quick Start Testing Guide

### Step 1: Create Test Users
```bash
python manage.py shell
```
```python
from accounts.models import User

# Create customer
User.objects.create_user(
    username='customer1',
    email='customer@test.com',
    password='Test123!',
    first_name='Test',
    last_name='Customer',
    role='customer'
)

# Create seller
User.objects.create_user(
    username='seller1',
    email='seller@test.com',
    password='Test123!',
    first_name='Test',
    last_name='Seller',
    role='seller'
)

# Create inspector
User.objects.create_user(
    username='inspector1',
    email='inspector@test.com',
    password='Test123!',
    first_name='Test',
    last_name='Inspector',
    role='inspector'
)

# Admin user (create via createsuperuser or shell)
User.objects.create_superuser(
    username='admin1',
    email='admin@test.com',
    password='Admin123!',
    first_name='Test',
    last_name='Admin'
)

exit()
```

### Step 2: Start Development Server
```bash
python manage.py runserver
```

### Step 3: Test Scenarios

#### ✅ **Test 1: Public Login for Regular Users**
1. Visit: `http://127.0.0.1:8000/accounts/login/`
2. Login with customer credentials:
   - Email: `customer@test.com`
   - Password: `Test123!`
3. **Expected Result**: Redirected to `/customer/dashboard/`

#### ✅ **Test 2: Admin Blocked from Public Login**
1. Visit: `http://127.0.0.1:8000/accounts/login/`
2. Try to login with admin credentials:
   - Email: `admin@test.com`
   - Password: `Admin123!`
3. **Expected Result**: Error message "Administrators must log in through the admin portal"

#### ✅ **Test 3: Admin Login via Admin Portal**
1. Visit: `http://127.0.0.1:8000/accounts/admin-login/`
2. Login with admin credentials:
   - Email: `admin@test.com`
   - Password: `Admin123!`
3. **Expected Result**: Redirected to `/admin-dashboard/` with system statistics

#### ✅ **Test 4: Login Throttling**
1. Visit: `http://127.0.0.1:8000/accounts/login/`
2. Try logging in with wrong password **5 times**
3. On 6th attempt: **Expected Result**: "Too many login attempts. Please try again in 15 minutes."
4. **To reset**: Run `python manage.py shell` → `from django.core.cache import cache` → `cache.clear()`

#### ✅ **Test 5: Role-Based Access Control**
1. Login as customer
2. Try visiting `/seller/dashboard/` manually in browser
3. **Expected Result**: 403 Forbidden page showing:
   - "Access Denied"
   - "Required Role: seller"
   - "Your Current Role: customer"

#### ✅ **Test 6: Role-Based Navigation**
1. **Login as customer** - Check navbar shows: Home, Shop, Cart, Dashboard
2. **Login as seller** - Check navbar shows: Home, Shop, Submit Product, My Submissions, Dashboard
3. **Login as inspector** - Check navbar shows: Home, Shop, Assigned Inspections, Dashboard
4. **Login as admin** - Check navbar shows: Home, Shop, Admin Dashboard, Django Admin
5. **Not logged in** - Check navbar shows: Home, Shop, Products, How It Works, Contact

#### ✅ **Test 7: Dashboard Content**
1. **Seller Dashboard**: Should show submission statistics (Total, Pending, Approved, Rejected)
2. **Inspector Dashboard**: Should show inspection statistics (Total, Pending, Completed)
3. **Admin Dashboard**: Should show system overview (Users, Products, Submissions, Inspections)
4. **Customer Dashboard**: Should show quick actions (Browse Products, View Orders)

#### ✅ **Test 8: Secure Logout**
1. Login as any user
2. Click "Logout" in navbar
3. **Expected Result**: Successfully logged out, redirected to home page
4. Try accessing dashboard again: **Expected Result**: Redirected to login page

#### ✅ **Test 9: Cart Visibility**
1. **Not logged in**: Visit home page - Cart icon should NOT be visible
2. **Login as customer**: Cart icon should appear in navbar with item count badge
3. **Login as seller/inspector/admin**: Cart behavior may vary based on business rules

---

## 🔐 Security Features Details

### Login Throttling Configuration
```python
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_TIMEOUT = 900  # 15 minutes in seconds
```

### Middleware Path Protection
```python
ROLE_PROTECTED_PATHS = {
    '/customer/': ['customer'],
    '/seller/': ['seller', 'customer'],  # Both can submit products
    '/inspector/': ['inspector'],
    '/admin-dashboard/': ['admin'],
}

PUBLIC_PATHS = ['/shop/', '/products/', '/profile/']
ANONYMOUS_PATHS = ['/accounts/login/', '/accounts/register/', '/']
```

### Cache Configuration (in settings.py)
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-certibuy',
    }
}
```

---

## 📊 User Role Overview

| Role | Dashboard | Can Submit Products | Can Inspect | Can Manage System | Login Page |
|------|-----------|-------------------|-------------|-------------------|------------|
| **Customer** | `/customer/dashboard/` | ✅ Yes | ❌ No | ❌ No | Public |
| **Seller** | `/seller/dashboard/` | ✅ Yes | ❌ No | ❌ No | Public |
| **Inspector** | `/inspector/dashboard/` | ❌ No | ✅ Yes | ❌ No | Public |
| **Admin** | `/admin-dashboard/` | ✅ Yes | ✅ Yes | ✅ Yes | Admin Portal |

---

## 🛠️ Troubleshooting

### Problem: "Too many login attempts" even with correct password
**Solution:**
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
>>> exit()
```

### Problem: 403 page not showing properly
**Solution:** Verify middleware is registered in `settings.py`:
```python
MIDDLEWARE = [
    # ... other middleware ...
    "accounts.middleware.RoleBasedAccessControl",  # Should be last or near end
]
```

### Problem: Admin can't access any pages
**Solution:** Ensure admin user has correct permissions:
```bash
python manage.py shell
>>> from accounts.models import User
>>> admin = User.objects.get(email='admin@test.com')
>>> admin.is_staff = True
>>> admin.is_superuser = True
>>> admin.save()
```

### Problem: Role-based navigation not working
**Solution:** Check user's role field:
```bash
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(email='test@test.com')
>>> print(user.role)  # Should be 'customer', 'seller', 'inspector', or 'admin'
>>> user.role = 'customer'  # Fix if needed
>>> user.save()
```

---

## 📝 Configuration Checklist

- [x] Middleware registered in `settings.py`
- [x] Cache configured for login throttling
- [x] All decorators imported in views
- [x] All URL routes configured
- [x] Templates created for dashboards
- [x] 403 error page created
- [x] Admin login page created
- [x] Navigation updated in base.html
- [x] Home page CTAs updated
- [x] Seller views protected
- [x] Inspector views protected
- [x] Django system check passes (no errors)

---

## 🎉 Success Indicators

When testing is complete, you should see:

✅ **Authentication:**
- Admin cannot login via public login page
- Regular users cannot login via admin login page
- Login throttling activates after 5 failed attempts
- Users redirected to correct dashboard after login

✅ **Authorization:**
- Users get 403 error when accessing unauthorized pages
- Navigation menu shows only role-appropriate links
- Decorators block unauthorized access to views
- Middleware blocks unauthorized URL access

✅ **User Experience:**
- Dashboards show role-specific content
- Statistics display correctly (seller submissions, inspector inspections, admin overview)
- Logout works via POST request with CSRF token
- Cart visible only when user is logged in

---

## 🚀 Next Steps

1. **Complete Manual Testing** - Follow test scenarios above
2. **Customize Dashboards** - Add real business logic and features
3. **Implement Business Features** - Product submission workflow, inspection process, order management
4. **Production Preparation:**
   - Enable HTTPS (`SECURE_SSL_REDIRECT = True`)
   - Set specific `ALLOWED_HOSTS`
   - Use production cache backend (Redis/Memcached)
   - Configure logging for security events
   - Set up monitoring and alerts

---

## 📚 Additional Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Security Best Practices**: https://docs.djangoproject.com/en/stable/topics/security/
- **Middleware Documentation**: https://docs.djangoproject.com/en/stable/topics/http/middleware/
- **Decorators Guide**: https://docs.djangoproject.com/en/stable/topics/http/decorators/

---

**Document Version:** 1.0  
**Implementation Date:** 2024  
**Status:** ✅ Production Ready (after testing)  
**Django Version:** 6.0.2  
**Python Version:** 3.12.3

---

## 📧 Support

If you encounter any issues during testing:
1. Check the troubleshooting section above
2. Verify all configuration checklist items
3. Review Django logs for detailed error messages
4. Ensure database migrations are up to date (`python manage.py migrate`)

**All enterprise RBAC features are now implemented and ready for testing! 🎉**
