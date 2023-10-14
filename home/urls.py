from django.urls import path

from .views import (
    CartView,
    HomeView,
    LoginView,
    SignupView,
    add_to_cart,
    remove_from_cart,
)

app_name = "home"
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("cart/", CartView.as_view(), name="cart"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    # Methods to manipulate cart
    path("add-to-cart/<int:pk>", add_to_cart, name="add-to-cart"),
    path("remove-from-cart/<int:pk>", remove_from_cart, name="remove-from-cart"),
]
