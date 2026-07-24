from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CartModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username


class CartItemModel(models.Model):
    cart =  models.ForeignKey(CartModel, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("shop.ProductModel", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)