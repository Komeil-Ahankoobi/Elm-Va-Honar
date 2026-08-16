from django.contrib import admin
from .models import (
    OrderModel, 
    OrderItemsModel, 
    CoponModel, 
    UserAddressModel
)

# Register your models here.
@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_price",
        "copon",
        "status",
        "created_date"
    )
    search_fields = ("id", "user__username", "user__phone_number", "copon__code")
    autocomplete_fields = ["user", "copon"]  # ← قابلیت سرچ برای کاربر و کوپن


@admin.register(OrderItemsModel)
class OrderItemsModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
        "created_date"
    )
    search_fields = ("order__id", "order__user__username", "order__user__phone_number", "product__title")
    autocomplete_fields = ["order", "product"]  # ← قابلیت سرچ برای سفارش و محصول


@admin.register(CoponModel)
class CoponModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "discount_percent",
        "max_limit_usage",
        "used_by_count",
        "expiration_date",
        "created_date"
    )
    search_fields = ("code",)  # ← لازم است تا در OrderModelAdmin قابل autocomplete باشد
    
    def used_by_count(self, obj):
        return obj.used_by.all().count()


@admin.register(UserAddressModel)
class UserAddressModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "state",
        "city",
        "zip_code",
        "created_date"
    )
    search_fields = ("user__username", "user__phone_number", "state", "city")
    autocomplete_fields = ["user"]  # ← قابلیت سرچ برای کاربر