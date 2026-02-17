from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.http import HttpResponseForbidden
from django.core.cache import cache
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, AddressForm
from .decorators import customer_required, seller_required, inspector_required, admin_required
from .models import Address, WishlistItem


# Login attempt throttling
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_TIMEOUT = 900  # 15 minutes


def _get_client_ip(request):
    """Get client IP address for rate limiting"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _check_login_attempts(ip_address):
    """Check if IP has exceeded login attempts"""
    cache_key = f'login_attempts_{ip_address}'
    attempts = cache.get(cache_key, 0)
    return attempts >= MAX_LOGIN_ATTEMPTS


def _increment_login_attempts(ip_address):
    """Increment failed login attempts"""
    cache_key = f'login_attempts_{ip_address}'
    attempts = cache.get(cache_key, 0)
    cache.set(cache_key, attempts + 1, LOGIN_ATTEMPT_TIMEOUT)


def _reset_login_attempts(ip_address):
    """Reset login attempts on successful login"""
    cache_key = f'login_attempts_{ip_address}'
    cache.delete(cache_key)


@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
def login_view(request):
    """Public login for customers, sellers, and inspectors"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    ip_address = _get_client_ip(request)
    
    if request.method == 'POST':
        # Check login attempt throttling
        if _check_login_attempts(ip_address):
            messages.error(request, 'Too many login attempts. Please try again later.')
            return render(request, 'accounts/login.html', {
                'form': CustomAuthenticationForm(),
                'locked': True
            })
        
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Prevent admin/staff from using public login
                if user.is_staff or user.is_superuser:
                    _increment_login_attempts(ip_address)
                    messages.error(request, 'Admin users must login through the Admin Panel.')
                    return redirect('accounts:admin_login')
                
                # Reset login attempts on successful login
                _reset_login_attempts(ip_address)
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Role-based dashboard redirect
                return redirect_by_role(user)
        else:
            _increment_login_attempts(ip_address)
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
def admin_login_view(request):
    """Separate login page for admin users only"""
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin:index')
        else:
            logout(request)
    
    ip_address = _get_client_ip(request)
    
    if request.method == 'POST':
        # Check login attempt throttling
        if _check_login_attempts(ip_address):
            messages.error(request, 'Too many login attempts. Please try again later.')
            return render(request, 'accounts/admin_login.html', {
                'form': CustomAuthenticationForm(),
                'locked': True
            })
        
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Only allow admin/staff to login here
                if not (user.is_staff or user.is_superuser):
                    _increment_login_attempts(ip_address)
                    messages.error(request, 'This login is for administrators only.')
                    return render(request, 'accounts/admin_login.html', {'form': form})
                
                # Reset login attempts on successful login
                _reset_login_attempts(ip_address)
                login(request, user)
                messages.success(request, f'Welcome Admin, {user.username}!')
                return redirect('admin:index')
        else:
            _increment_login_attempts(ip_address)
            messages.error(request, 'Invalid admin credentials.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/admin_login.html', {'form': form})


def redirect_by_role(user):
    """Redirect user to appropriate dashboard based on role"""
    if user.is_staff or user.is_superuser:
        return redirect('core:admin-dashboard')
    
    role_redirects = {
        'customer': 'core:shop',
        'seller': 'core:seller-dashboard',
        'inspector': 'core:inspector-dashboard',
    }
    
    dashboard_url = role_redirects.get(user.role, 'core:home')
    return redirect(dashboard_url)


@require_http_methods(["POST"])
@login_required
@csrf_protect
def logout_view(request):
    """Secure logout with CSRF protection"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')


@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
def register_view(request):
    """Public registration for customers and sellers"""
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to CertiBuy, {user.username}!')
            return redirect_by_role(user)
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """User profile - accessible to all authenticated users"""
    from sellers.models import SellerSubmission
    from inspections.models import Inspection
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'user': request.user,
        'form': form,
    }
    
    if request.user.role == 'seller':
        context['submission_count'] = SellerSubmission.objects.filter(seller=request.user).count()
        context['recent_submissions'] = SellerSubmission.objects.filter(seller=request.user)[:5]
    
    if request.user.role == 'inspector':
        context['inspection_count'] = Inspection.objects.filter(inspector=request.user).count()
        context['recent_inspections'] = Inspection.objects.filter(inspector=request.user)[:5]
    
    return render(request, 'accounts/profile.html', context)


@customer_required
def addresses_list(request):
    addresses = Address.objects.filter(user=request.user)
    context = {
        'addresses': addresses,
    }
    return render(request, 'accounts/addresses_list.html', context)


@customer_required
@require_http_methods(["GET", "POST"])
def address_create(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('accounts:addresses')
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {'form': form, 'form_title': 'Add Address'})


@customer_required
@require_http_methods(["GET", "POST"])
def address_update(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('accounts:addresses')
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/address_form.html', {'form': form, 'form_title': 'Edit Address'})


@customer_required
@require_http_methods(["POST"])
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, 'Address removed successfully.')
    return redirect('accounts:addresses')


@customer_required
@require_http_methods(["POST"])
def address_set_default(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, 'Default address updated.')
    return redirect('accounts:addresses')


@customer_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product').prefetch_related('product__images')
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'accounts/wishlist.html', context)

