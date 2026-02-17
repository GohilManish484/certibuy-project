"""
Secure Admin Configuration
Apply these security measures to Django admin panel
"""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


class SecureAdminSite(admin.AdminSite):
    """Custom admin site with enhanced security"""
    
    site_header = 'CertiBuy Admin Portal'
    site_title = 'CertiBuy Admin'
    index_title = 'Administration Dashboard'
    
    def has_permission(self, request):
        """Only allow staff and superusers"""
        return request.user.is_active and (request.user.is_staff or request.user.is_superuser)


# Configuration guide for settings.py:
# Add the following to restrict admin access:
"""
# Admin Security
ADMIN_ENABLED = True  # Set to False to disable admin panel in production
SECURE_ADMIN_PATH = os.environ.get('ADMIN_PATH', 'admin')  # Use env variable for custom path

# In urls.py, use:
# path(f"{settings.SECURE_ADMIN_PATH}/", admin.site.urls),
"""

# Best practices:
# 1. Use strong admin passwords (enforced by password validators)
# 2. Enable 2FA for admin users (external package required)
# 3. Limit admin access by IP (middleware implementation)
# 4. Monitor admin login attempts (logging configured)
# 5. Use custom admin URL path (not 'admin/')
# 6. Disable admin autodiscover in production if not needed
