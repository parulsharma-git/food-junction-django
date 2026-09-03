from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:item_id>/", views.cart_add, name="cart_add"),
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("cart/promo/", views.cart_promo, name="cart_promo"),
    path("buy-now/<int:item_id>/", views.buy_now, name="buy_now"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/success/<str:order_id>/", views.order_success, name="order_success"),
]
