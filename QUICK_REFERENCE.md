# 🚀 CertiBuy RBAC - Quick Reference Card

## ⚡ Fast Testing Guide

### 1️⃣ Create Users (One Command)
```bash
python manage.py shell -c "
from accounts.models import User
User.objects.filter(email__endswith='@test.com').delete()
User.objects.create_user(username='customer1', email='customer@test.com', password='Test123!', role='customer', first_name='Test', last_name='Customer')
User.objects.create_user(username='seller1', email='seller@test.com', password='Test123!', role='seller', first_name='Test', last_name='Seller')
User.objects.create_user(username='inspector1', email='inspector@test.com', password='Test123!', role='inspector', first_name='Test', last_name='Inspector')
User.objects.create_superuser(username='admin1', email='admin@test.com', password='Admin123!', first_name='Admin', last_name='User')
print('✅ All test users created!')
"
```

### 2️⃣ Start Server
```bash
python manage.py runserver
```

### 3️⃣ Test Credentials

| Role | Email | Password | Dashboard URL |
|------|-------|----------|---------------|
| **Customer** | customer@test.com | Test123! | /customer/dashboard/ |
| **Seller** | seller@test.com | Test123! | /seller/dashboard/ |
| **Inspector** | inspector@test.com | Test123! | /inspector/dashboard/ |
| **Admin** | admin@test.com | Admin123! | /admin-dashboard/ |

---

## 🎯 Quick Test Scenarios

### ✅ Test 1: Role Separation (2 min)
```
1. Login as customer (customer@test.com / Test123!)
2. Try visiting: http://127.0.0.1:8000/seller/dashboard/
   → Expected: 403 Forbidden page ✅
```

### ✅ Test 2: Admin Blocking (1 min)
```
1. Visit: http://127.0.0.1:8000/accounts/login/
2. Try admin login (admin@test.com / Admin123!)
   → Expected: "Administrators must use admin portal" ✅
3. Visit: http://127.0.0.1:8000/accounts/admin-login/
4. Login with admin credentials
   → Expected: Access to admin dashboard ✅
```

### ✅ Test 3: Login Throttling (2 min)
```
1. Visit: http://127.0.0.1:8000/accounts/login/
2. Try wrong password 5 times for any user
3. 6th attempt → Expected: "Too many login attempts" ✅
4. Clear cache: python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

### ✅ Test 4: Navigation Menu (1 min)
```
Login as each role and verify navbar:
- Customer    → Home | Shop | Cart | Dashboard ✅
- Seller      → Home | Shop | Submit Product | My Submissions | Dashboard ✅
- Inspector   → Home | Shop | Assigned Inspections | Dashboard ✅
- Admin       → Home | Shop | Admin Dashboard | Django Admin ✅
```

### ✅ Test 5: Dashboards (2 min)
```
Visit each dashboard after login:
- /customer/dashboard/   → Quick actions cards ✅
- /seller/dashboard/     → Submission statistics ✅
- /inspector/dashboard/  → Inspection statistics ✅
- /admin-dashboard/      → Full system overview ✅
```

---

## 🔐 Security Features

### Login Throttling
- **Max Attempts**: 5
- **Lockout Time**: 15 minutes
- **Tracked By**: IP address
- **Clear Cache**: `python manage.py shell -c "from django.core.cache import cache; cache.clear()"`

### Access Control Layers
1. **Middleware**: Global path protection (all requests)
2. **Decorators**: View-level protection (specific functions)
3. **Template Logic**: UI element visibility (conditional rendering)

### Authentication Portals
- **Public Login** (`/accounts/login/`): Customer | Seller | Inspector
- **Admin Login** (`/accounts/admin-login/`): Admin only

---

## 📋 URL Map

```
PUBLIC ROUTES (no auth required):
  /                          → Home page
  /shop/                     → Product listing
  /accounts/login/           → Public login
  /accounts/admin-login/     → Admin login
  /accounts/register/        → User registration

AUTHENTICATED ROUTES (role-specific):
  /customer/dashboard/       → Customer dashboard (customer only)
  /seller/dashboard/         → Seller dashboard (seller only)
  /inspector/dashboard/      → Inspector dashboard (inspector only)
  /admin-dashboard/          → Admin dashboard (admin only)
  /accounts/profile/         → User profile (all logged-in users)
  /accounts/logout/          → Logout (POST only)
  
SELLER ROUTES:
  /sellers/submit/           → Submit product (seller + customer)
  /sellers/my-submissions/   → View submissions (seller + customer)
  
INSPECTOR ROUTES:
  /inspections/              → Inspection list (inspector + admin)
  /inspections/<id>/         → Inspection detail (inspector + admin)
```

---

## 🛠️ Troubleshooting Commands

### Reset Login Attempts
```bash
python manage.py shell -c "from django.core.cache import cache; cache.clear(); print('✅ Cache cleared')"
```

### Check User Role
```bash
python manage.py shell -c "from accounts.models import User; u = User.objects.get(email='customer@test.com'); print(f'Role: {u.role}')"
```

### Fix Admin Permissions
```bash
python manage.py shell -c "from accounts.models import User; u = User.objects.get(email='admin@test.com'); u.is_staff = True; u.is_superuser = True; u.save(); print('✅ Admin permissions fixed')"
```

### Delete Test Users
```bash
python manage.py shell -c "from accounts.models import User; User.objects.filter(email__endswith='@test.com').delete(); print('✅ Test users deleted')"
```

### Run System Check
```bash
python manage.py check
```

---

## 📊 Dashboard Features

### Customer Dashboard
- Quick action cards
- Browse products link
- View orders link
- Profile link

### Seller Dashboard
**Statistics:**
- Total Submissions
- Pending (yellow badge)
- Approved (green badge)
- Rejected (red badge)

**Quick Actions:**
- Submit New Product
- View All Submissions
- Manage Profile

**Recent Submissions Table:**
- Product Name
- Category
- Status with color-coded badges
- Submission Date
- Action links

### Inspector Dashboard
**Statistics:**
- Total Inspections
- Pending
- Completed

**Quick Actions:**
- View All Inspections
- Manage Profile

**Recent Inspections Table:**
- Product Name
- Seller
- Status
- Inspection Date
- Action links

### Admin Dashboard
**User Statistics:**
- Total Users
- Customers count
- Sellers count
- Inspectors count

**Product Statistics:**
- Total Products
- Certified Products

**Submission Statistics:**
- Total Submissions
- Pending Submissions

**Inspection Statistics:**
- Total Inspections
- Pending Inspections

**Admin Actions:**
- Manage Users
- Manage Products
- Manage Submissions
- Manage Inspections
- Access Django Admin

**Recent Activity:**
- Recent Submissions feed
- Recent Inspections feed

---

## ✅ Pre-Production Checklist

- [ ] All manual tests pass
- [ ] No Django system check errors
- [ ] Test users created and working
- [ ] All dashboards display correctly
- [ ] 403 page renders properly
- [ ] Login throttling works
- [ ] Navigation menu updates per role
- [ ] Logout requires POST method
- [ ] Admin separated from regular login
- [ ] Cart visibility works correctly

### For Production Deployment:
- [ ] Set `DEBUG = False`
- [ ] Configure specific `ALLOWED_HOSTS`
- [ ] Enable HTTPS security settings
- [ ] Use Redis/Memcached for cache
- [ ] Set up monitoring and logging
- [ ] Configure email backend
- [ ] Run security audit
- [ ] Set up backup system

---

## 🎉 Quick Win Verification

Run these 3 tests to confirm everything works:

### ✅ Test A: Basic Auth (30 seconds)
```
1. Visit http://127.0.0.1:8000/accounts/login/
2. Login: customer@test.com / Test123!
3. Should see customer dashboard ✅
```

### ✅ Test B: Access Control (30 seconds)
```
1. While logged in as customer
2. Visit http://127.0.0.1:8000/seller/dashboard/
3. Should see 403 Forbidden page ✅
```

### ✅ Test C: Admin Separation (30 seconds)
```
1. Logout
2. Visit http://127.0.0.1:8000/accounts/admin-login/
3. Login: admin@test.com / Admin123!
4. Should see admin dashboard with statistics ✅
```

**All 3 pass?** → ✅ **System is working perfectly!**

---

## 📚 Documentation Files

1. **QUICK_REFERENCE.md** (this file) - Fast testing guide
2. **RBAC_IMPLEMENTATION_GUIDE.md** - Detailed testing with explanations
3. **IMPLEMENTATION_SUMMARY.md** - High-level overview and architecture

---

## 💡 Pro Tips

1. **Keep a browser tab for each role** to quickly test cross-role access
2. **Use private/incognito windows** for testing multiple users simultaneously
3. **Check browser console** for JavaScript errors (should be none)
4. **Check Django console** for server errors (should be none)
5. **Test on mobile** to verify responsive navbar

---

**Last Updated:** 2024  
**Status:** ✅ Ready for Testing  
**Estimated Testing Time:** 10-15 minutes

🚀 **Happy Testing!**
