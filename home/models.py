from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse

# Create your models here.


class Item(models.Model):
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=120)
    price = models.FloatField()
    stock_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("home:HomeView", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("home:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("home:remove-from-cart", kwargs={"slug": self.slug})


class Cart(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    pass


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)


class CartItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.cart.id) + " - " + self.item.name
