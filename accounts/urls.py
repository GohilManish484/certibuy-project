from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url=reverse_lazy('accounts:profile')
    ), name='password_change'),
    path('addresses/', views.addresses_list, name='addresses'),
    path('addresses/add/', views.address_create, name='address_add'),
    path('addresses/<int:pk>/edit/', views.address_update, name='address_edit'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
    path('addresses/<int:pk>/default/', views.address_set_default, name='address_default'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
]
