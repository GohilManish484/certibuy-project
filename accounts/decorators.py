from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string


def access_denied_response(request, required_role=None):
    """Generate 403 Forbidden response"""
    status_code = 403
    template_name = 'errors/403.html'
    context = {
        'user': request.user,
        'required_role': required_role,
    }
    return HttpResponseForbidden(render_to_string(template_name, context, request=request))


def login_required_custom(view_func):
    """Requires user to be logged in"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'You must login first.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def customer_required(view_func):
    """Restrict access to customers only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'You must login as a customer.')
            return redirect('accounts:login')
        
        if request.user.role != 'customer':
            messages.error(request, 'You do not have permission to access this page.')
            return access_denied_response(request, 'customer')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def seller_required(view_func):
    """Restrict access to sellers only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'You must login as a seller.')
            return redirect('accounts:login')
        
        if request.user.role != 'seller':
            messages.error(request, 'You do not have permission to access this page.')
            return access_denied_response(request, 'seller')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def inspector_required(view_func):
    """Restrict access to inspectors only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'You must login as an inspector.')
            return redirect('accounts:login')
        
        if request.user.role != 'inspector':
            messages.error(request, 'You do not have permission to access this page.')
            return access_denied_response(request, 'inspector')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Restrict access to admins only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Admin access required.')
            return redirect('accounts:admin_login')
        
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'You do not have admin access.')
            return access_denied_response(request, 'admin')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """
    Restrict access to specific roles
    Usage: @role_required('customer', 'seller')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'You must login.')
                return redirect('accounts:login')
            
            # Admin has access to everything
            if request.user.is_staff or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if request.user.role not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return access_denied_response(request, ', '.join(allowed_roles))
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
