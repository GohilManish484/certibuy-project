from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("shop/", views.ShopView.as_view(), name="shop"),
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/update/", views.update_cart, name="update_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path("return-policy/", views.ReturnPolicyView.as_view(), name="return_policy"),
    path("how-it-works/", views.HowItWorksView.as_view(), name="how_it_works"),
    path("search/suggest/", views.search_suggestions, name="search_suggestions"),
    
    # Role-based dashboards
    path("customer/dashboard/", views.customer_dashboard, name="customer-dashboard"),
    path("seller/dashboard/", views.seller_dashboard, name="seller-dashboard"),
    path("inspector/dashboard/", views.inspector_dashboard, name="inspector-dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin-dashboard"),
    path("admin-dashboard/notifications/", views.admin_notification_dashboard, name="admin-notification-dashboard"),
    path("admin-dashboard/notifications/data/", views.admin_notification_data, name="admin-notification-data"),
    path("admin-dashboard/notifications/mark-read/", views.admin_notification_mark_read, name="admin-notification-mark-read"),
]
