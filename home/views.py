from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, View

from .models import Cart, CartItem, Customer, Item


def init_cart(request: HttpRequest):
    try:
        cart_id = request.session["cart_id"]
        cart = Cart.objects.get(pk=cart_id)
    except (KeyError, Cart.DoesNotExist):
        cart = Cart.objects.create()
        cart.save()
        request.session["cart_id"] = cart.id
    count = CartItem.objects.filter(cart=cart).aggregate(Sum("quantity"))[
        "quantity__sum"
    ]
    total_cart_items = count if count else 0
    return cart, total_cart_items


def add_to_cart(request: HttpRequest, pk):
    cart, total_cart_items = init_cart(request)
    item = get_object_or_404(Item, pk=pk)

    try:
        cart_item = CartItem.objects.get(item=item, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(item=item, cart=cart)
    return redirect("home:home")


# delete item from cart
def remove_from_cart(request: HttpRequest, pk):
    cart, total_cart_items = init_cart(request)
    item = get_object_or_404(Item, pk=pk)

    try:
        cart_item = CartItem.objects.get(item_id=item, cart=cart)
        item_count = cart_item.quantity
        if item_count == 1:
            cart_item.delete()
            pass
        else:
            cart_item.quantity -= 1
            cart_item.save()
    except CartItem.DoesNotExist:
        pass
    return redirect("home:cart")


class HomeView(ListView):
    def get(self, *args, **kwargs):
        cart, total_cart_items = init_cart(self.request)
        context = {
            "items": Item.objects.all(),
            "cart_item_count": total_cart_items,
        }
        return render(self.request, "home.html", context)


class CartView(ListView):
    def get(self, *args, **kwargs):
        cart, total_cart_items = init_cart(self.request)
        context = {
            "cartItems": CartItem.objects.filter(cart=cart),
            "cart_item_count":total_cart_items,
        }
        return render(self.request, "cart.html", context)


class SignupView(View):
    def get(self, *args, **kwargs):
        cart, total_cart_items = init_cart(self.request)
        context = {
            "cart_item_count": total_cart_items,
        }
        return render(self.request, "signup.html", context)

    def post(self, *args, **kwargs):
        name = self.request.POST.get("name")
        username = self.request.POST.get("username")
        password = self.request.POST.get("password")

        cart, _ = init_cart(self.request)
        user = User.objects.create_user(username=username, password=password, first_name=name)
        user.save()
        customer = Customer.objects.create(user=user, cart=cart)
        customer.save()
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return redirect("home:home")


class LoginView(View):
    def get(self, *args, **kwargs):
        cart, total_cart_items = init_cart(self.request)
        context = {
            "cart_item_count": total_cart_items,
        }
        return render(self.request, "login.html", context)

    def post(self, *args, **kwargs):
        username = self.request.POST.get("username")
        password = self.request.POST.get("password")
        print(username, password)

        user = authenticate(username=username, password=password)
        login(self.request, user)

        if user is None:
            # auth err
            return redirect("home:login")

        # logic to merge cartlocal and pre-registered carts
        customer = Customer.objects.get(user=user)
        cust_cart = customer.cart

        cart, _ = init_cart(self.request)
        cart_items = CartItem.objects.filter(cart=cart)
        for cart_item in cart_items:
            try:
                cust_cart_item = CartItem.objects.get(
                    item=cart_item.item, cart=cust_cart
                )
                cust_cart_item.quantity += 1
                cust_cart_item.save()
                cart_item.delete()
            except CartItem.DoesNotExist:
                cart_item.cart = cust_cart
                cart_item.save()
        self.request.session["cart_id"] = cust_cart.id
        return redirect("home:home")
