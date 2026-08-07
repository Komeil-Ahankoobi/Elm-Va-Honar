from django.db import models
from django.contrib.auth.models import User

from shop.models import ProductVarientModel

# Create your models here.
class CartModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username
    
    def calculate_total_price(self):
        return sum(item.product.get_price() * item.quantity for item in self.cart_items.all())


class CartItemModel(models.Model):
    cart =  models.ForeignKey(CartModel, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("shop.ProductModel", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)
    variant = models.ForeignKey(
        ProductVarientModel, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product", "variant"],
                name="unique_cart_product_variant"
            )
        ]