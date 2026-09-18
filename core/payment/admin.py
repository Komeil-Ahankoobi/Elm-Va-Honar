from django.contrib import admin

from .models import PaymentModel


@admin.register(PaymentModel)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "order_id",
        "amount",
        "status",
        "authority_id",
        "ref_id",
        "created_date",
        "updated_date",
    )

    list_filter = (
        "status",
        "created_date",
    )

    # امکان جستجو بر اساس ID سفارش
    search_fields = (
        "order__id",
        "authority_id",
        "ref_id",
    )

    # اطلاعات حساس/تولیدشده توسط درگاه فقط خواندنی باشند
    readonly_fields = (
        "authority_id",
        "ref_id",
        "amount",
        "card_pan",
        "card_hash",
        "response_json",
        "response_code",
        "created_date",
        "updated_date",
    )

    @admin.display(description="Order ID", ordering="order__id")
    def order_id(self, obj):
        return obj.order_id
