from django.contrib import admin
from .models import OrderModel, OrderItemsModel, CoponModel, UserAddressModel
from django import forms
from .widgets import JalaliDateTimeField

@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_user_fullname",
        "total_price",
        "copon",
        "status",
        "created_date",
    )

    # ادمین می‌تواند وضعیت سفارش را مستقیماً از لیست سفارش‌ها تغییر دهد.
    list_editable = ("status",)

    # فیلتر سریع سفارش‌ها بر اساس وضعیت
    list_filter = (
        "status",
        "created_date",
    )

    search_fields = (
        "=id",
        "copon__code",
        "user__username",
    )
    autocomplete_fields = ["user", "copon"]

    @admin.display(description="نام و نام خانوادگی")
    def get_user_fullname(self, obj):
        if hasattr(obj.user, "user_profile"):
            return obj.user.user_profile.get_fullname()
        return "بدون پروفایل"


@admin.register(OrderItemsModel)
class OrderItemsModelAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price", "created_date")
    search_fields = (
        "=order__id",
        "order__user__username",
        "product__title",
    )
    autocomplete_fields = ["order", "product"]


class CoponModelAdminForm(forms.ModelForm):
    expiration_date = JalaliDateTimeField(
        required=False,
        label="تاریخ انقضا (شمسی)",
        help_text="فرمت: ۱۴۰۳/۰۶/۲۷ ۱۴:۳۰"
    )

    class Meta:
        model = CoponModel
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "used_by" in self.fields:
            self.fields["used_by"].label_from_instance = self.get_user_label

    @staticmethod
    def get_user_label(user_obj):
        if hasattr(user_obj, "user_profile"):
            fullname = user_obj.user_profile.get_fullname()
            if fullname and fullname != "کاربر جدید":
                return f"{fullname}"
        return user_obj.username


@admin.register(CoponModel)
class CoponModelAdmin(admin.ModelAdmin):
    form = CoponModelAdminForm
    list_display = (
        "id",
        "code",
        "discount_percent",
        "max_limit_usage",
        "used_by_count",
        "expiration_date",
        "created_date",
    )
    search_fields = ("code",)

    def used_by_count(self, obj):
        return obj.used_by.count()


@admin.register(UserAddressModel)
class UserAddressModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "state", "city", "zip_code", "created_date")
    search_fields = (
        "user__username",
        "state",
        "city",
    )
    autocomplete_fields = ["user"]
