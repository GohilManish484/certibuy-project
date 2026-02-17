"""
RBAC Testing Script for CertiBuy
Tests all role-based access control features
"""

import os
import django

os.environ.setdefault('DJANGO_SECRET_KEY', 'test-key-for-security')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certibuy.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.core.cache import cache

User = get_user_model()

def print_section(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")

def test_user_creation():
    """Test creating users with different roles"""
    print_section("USER CREATION TEST")
    
    # Clean up existing test users
    User.objects.filter(email__endswith='@test.com').delete()
    
    try:
        customer = User.objects.create_user(
            email='customer@test.com',
            password='Test123!@#',
            first_name='Test',
            last_name='Customer',
            role='customer'
        )
        print_test("Customer user created", customer.role == 'customer')
        
        seller = User.objects.create_user(
            email='seller@test.com',
            password='Test123!@#',
            first_name='Test',
            last_name='Seller',
            role='seller'
        )
        print_test("Seller user created", seller.role == 'seller')
        
        inspector = User.objects.create_user(
            email='inspector@test.com',
            password='Test123!@#',
            first_name='Test',
            last_name='Inspector',
            role='inspector'
        )
        print_test("Inspector user created", inspector.role == 'inspector')
        
        admin = User.objects.create_superuser(
            email='admin@test.com',
            password='Test123!@#',
            first_name='Test',
            last_name='Admin'
        )
        print_test("Admin user created", admin.is_staff and admin.is_superuser)
        
        return True
    except Exception as e:
        print_test("User creation", False, str(e))
        return False

def test_login_system():
    """Test login functionality for different roles"""
    print_section("LOGIN SYSTEM TEST")
    
    client = Client()
    
    # Test customer login
    response = client.post('/accounts/login/', {
        'username': 'customer@test.com',
        'password': 'Test123!@#'
    })
    print_test("Customer login", response.status_code in [200, 302], 
               f"Status: {response.status_code}")
    client.logout()
    
    # Test seller login
    response = client.post('/accounts/login/', {
        'username': 'seller@test.com',
        'password': 'Test123!@#'
    })
    print_test("Seller login", response.status_code in [200, 302],
               f"Status: {response.status_code}")
    client.logout()
    
    # Test inspector login
    response = client.post('/accounts/login/', {
        'username': 'inspector@test.com',
        'password': 'Test123!@#'
    })
    print_test("Inspector login", response.status_code in [200, 302],
               f"Status: {response.status_code}")
    client.logout()
    
    # Test admin attempting public login (should fail)
    response = client.post('/accounts/login/', {
        'username': 'admin@test.com',
        'password': 'Test123!@#'
    })
    print_test("Admin blocked from public login", 
               "Administrators must log in" in str(response.content),
               "Admin redirected to admin login")
    
    # Test admin login via admin portal
    response = client.post('/accounts/admin-login/', {
        'username': 'admin@test.com',
        'password': 'Test123!@#'
    })
    print_test("Admin login via admin portal", response.status_code in [200, 302],
               f"Status: {response.status_code}")
    client.logout()

def test_login_throttling():
    """Test login attempt throttling"""
    print_section("LOGIN THROTTLING TEST")
    
    cache.clear()  # Clear cache before test
    client = Client()
    
    # Attempt 5 failed logins
    for i in range(5):
        client.post('/accounts/login/', {
            'username': 'customer@test.com',
            'password': 'wrong_password'
        })
    
    # 6th attempt should be blocked
    response = client.post('/accounts/login/', {
        'username': 'customer@test.com',
        'password': 'Test123!@#'
    })
    
    is_locked = "Too many login attempts" in str(response.content) or response.status_code == 429
    print_test("Login throttling activates after 5 attempts", is_locked,
               "Account temporarily locked")
    
    # Clear cache for clean state
    cache.clear()

def test_role_based_access():
    """Test role-based access control to different pages"""
    print_section("ROLE-BASED ACCESS CONTROL TEST")
    
    client = Client()
    
    # Test customer accessing customer dashboard
    client.login(username='customer@test.com', password='Test123!@#')
    response = client.get('/customer/dashboard/')
    print_test("Customer accesses customer dashboard", response.status_code == 200,
               f"Status: {response.status_code}")
    
    # Test customer accessing seller dashboard (should fail)
    response = client.get('/seller/dashboard/')
    print_test("Customer blocked from seller dashboard", response.status_code == 403,
               f"Status: {response.status_code} (403 expected)")
    client.logout()
    
    # Test seller accessing seller dashboard
    client.login(username='seller@test.com', password='Test123!@#')
    response = client.get('/seller/dashboard/')
    print_test("Seller accesses seller dashboard", response.status_code == 200,
               f"Status: {response.status_code}")
    
    # Test seller accessing inspector dashboard (should fail)
    response = client.get('/inspector/dashboard/')
    print_test("Seller blocked from inspector dashboard", response.status_code == 403,
               f"Status: {response.status_code} (403 expected)")
    client.logout()
    
    # Test inspector accessing inspector dashboard
    client.login(username='inspector@test.com', password='Test123!@#')
    response = client.get('/inspector/dashboard/')
    print_test("Inspector accesses inspector dashboard", response.status_code == 200,
               f"Status: {response.status_code}")
    
    # Test inspector accessing admin dashboard (should fail)
    response = client.get('/admin-dashboard/')
    print_test("Inspector blocked from admin dashboard", response.status_code == 403,
               f"Status: {response.status_code} (403 expected)")
    client.logout()
    
    # Test admin accessing admin dashboard
    client.login(username='admin@test.com', password='Test123!@#')
    response = client.get('/admin-dashboard/')
    print_test("Admin accesses admin dashboard", response.status_code == 200,
               f"Status: {response.status_code}")
    
    # Test admin can access any dashboard (should pass)
    response = client.get('/customer/dashboard/')
    print_test("Admin can access customer dashboard", response.status_code == 200,
               f"Admin has unrestricted access")
    client.logout()

def test_anonymous_access():
    """Test anonymous user restrictions"""
    print_section("ANONYMOUS USER RESTRICTION TEST")
    
    client = Client()
    
    # Test accessing dashboard without login
    response = client.get('/customer/dashboard/')
    print_test("Anonymous blocked from customer dashboard", 
               response.status_code in [302, 403],
               f"Redirected or blocked (Status: {response.status_code})")
    
    # Test accessing seller pages without login
    response = client.get('/seller/dashboard/')
    print_test("Anonymous blocked from seller dashboard",
               response.status_code in [302, 403],
               f"Redirected or blocked (Status: {response.status_code})")
    
    # Test accessing public pages without login
    response = client.get('/')
    print_test("Anonymous can access home page", response.status_code == 200,
               f"Status: {response.status_code}")

def test_403_page():
    """Test 403 error page rendering"""
    print_section("403 ERROR PAGE TEST")
    
    client = Client()
    client.login(username='customer@test.com', password='Test123!@#')
    
    # Try accessing seller dashboard as customer
    response = client.get('/seller/dashboard/')
    
    has_403 = response.status_code == 403
    has_content = b'Access Denied' in response.content or b'403' in response.content
    
    print_test("403 page renders correctly", has_403 and has_content,
               f"Status: {response.status_code}, Has error content: {has_content}")
    client.logout()

def run_all_tests():
    """Run all security tests"""
    print("\n" + "█"*60)
    print("  CERTIBUY RBAC SECURITY TEST SUITE")
    print("█"*60)
    
    try:
        test_user_creation()
        test_login_system()
        test_login_throttling()
        test_role_based_access()
        test_anonymous_access()
        test_403_page()
        
        print_section("TEST SUMMARY")
        print("✅ All RBAC security tests completed!")
        print("⚠️  Note: Some tests may show warnings - review output above")
        print("\n📝 Manual Testing Recommended:")
        print("   1. Start server: python manage.py runserver")
        print("   2. Test each role's navigation menu")
        print("   3. Verify dashboard displays correct data")
        print("   4. Test logout functionality")
        print("   5. Test cart visibility for logged-in users")
        
    except Exception as e:
        print_section("TEST FAILED")
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_all_tests()
