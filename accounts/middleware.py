"""
Role-Based Access Control Middleware
Enforces security rules globally and prevents unauthorized access

Protected paths are defined by role mapping.
Unauthorized access is blocked with 403 response.
"""

from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.deprecation import MiddlewareMixin


class RoleBasedAccessControl(MiddlewareMixin):
    """
    Middleware to enforce Role-Based Access Control (RBAC)
    
    Defines protected paths and enforces role restrictions globally.
    """
    
    # Path prefixes protected by role
    ROLE_PROTECTED_PATHS = {
        '/customer/': ['customer'],
        '/seller/': ['seller'],
        '/inspector/': ['inspector'],
        '/admin/': ['admin'],
        '/admin-dashboard/': ['admin'],
        '/inspections/': ['inspector', 'admin'],
        '/orders/': ['customer', 'admin'],
    }
    
    # Public paths - accessible to all authenticated users
    PUBLIC_PATHS = [
        '/shop/',
        '/products/',
        '/accounts/profile/',
        '/accounts/logout/',
        '/core/cart/',
        '/core/',
    ]
    
    # Completely public paths - no authentication required
    ANONYMOUS_PATHS = [
        '/accounts/login/',
        '/accounts/register/',
        '/accounts/admin-login/',
        '/admin/',
        '/static/',
        '/media/',
        '/',
    ]
    
    def process_request(self, request):
        """Check permissions before processing request"""
        path = request.path
        user = request.user
        
        # Allow anonymous paths
        if self._is_anonymous_path(path):
            return None
        
        # Require authentication for protected paths
        if not user.is_authenticated:
            # Check if trying to access protected content
            if not self._is_public_path(path):
                messages.warning(request, 'You must login to access this page.')
                return redirect('accounts:login')
            return None
        
        # Admin has unrestricted access
        if user.is_staff or user.is_superuser:
            return None
        
        # Check role-specific paths
        for protected_prefix, allowed_roles in self.ROLE_PROTECTED_PATHS.items():
            if path.startswith(protected_prefix):
                if user.role not in allowed_roles:
                    messages.error(request, 'You do not have permission to access this page.')
                    return self._get_forbidden_response(request, allowed_roles)
                return None
        
        return None
    
    def _is_anonymous_path(self, path):
        """Check if path is available to everyone"""
        return any(path.startswith(p) for p in self.ANONYMOUS_PATHS)
    
    def _is_public_path(self, path):
        """Check if path is available to authenticated users"""
        return any(path.startswith(p) for p in self.PUBLIC_PATHS)
    
    def _get_forbidden_response(self, request, required_roles):
        """Generate 403 Forbidden response"""
        context = {
            'user': request.user,
            'required_roles': required_roles,
        }
        html = render_to_string('errors/403.html', context, request=request)
        return HttpResponseForbidden(html)
