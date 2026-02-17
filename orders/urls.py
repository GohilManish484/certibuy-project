from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    # Buy Now
    path("buy-now/", views.buy_now, name="buy_now"),
    
    # 3-Step Checkout
    path("checkout/step-1/", views.checkout_step1_address, name="checkout_step1_address"),
    path("checkout/step-2/", views.checkout_step2_payment, name="checkout_step2_payment"),
    path("checkout/step-3/", views.checkout_step3_review, name="checkout_step3_review"),
    
    # Payment
    path("payment/<int:order_id>/", views.payment_gateway, name="payment_gateway"),
    path("payment/callback/", views.payment_callback, name="payment_callback"),
    
    # Order Management
    path("order/<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
    path("order/<int:order_id>/track/", views.order_tracking, name="order_tracking"),
    path("order/<int:order_id>/confirmation/", views.order_confirmation, name="order_confirmation"),
    path("order/<int:order_id>/invoice/", views.order_invoice, name="order_invoice"),
]
