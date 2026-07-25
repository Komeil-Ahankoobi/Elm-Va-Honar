from django.contrib import admin
from cart.models import CartItemModel, CartModel

@admin.register(CartItemModel)
class CartItemModelAdmin(admin.ModelAdmin):
    list_display = ("quantity", "cart", "product" )


@admin.register(CartModel)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ("user", )

