from django.db import models

from .gateways import GatewayType


class PaymentStatusType(models.IntegerChoices):
    pending = 1, "در انتظار"
    success = 2, "پرداخت موفق"
    failed = 3, "پرداخت ناموفق"


class PaymentModel(models.Model):
    order = models.ForeignKey(
        "order.OrderModel",
        on_delete=models.PROTECT,
        related_name="payments",
    )
    gateway = models.CharField(
        max_length=20,
        choices=GatewayType.choices,
        default=GatewayType.zarinpal.value,
        db_index=True,
    )
    # زرین‌پال: Authority  |  پارسیان: Token (به‌صورت رشته)
    authority_id = models.CharField(max_length=64, db_index=True)
    # زرین‌پال: ref_id  |  پارسیان: RRN
    ref_id = models.BigIntegerField(null=True, blank=True)
    # همیشه به «تومان» (واحد سایت)؛ تبدیل به ریال برای پارسیان موقع ارسال انجام می‌شود.
    amount = models.PositiveBigIntegerField(default=0)
    card_pan = models.CharField(max_length=32, blank=True)
    card_hash = models.CharField(max_length=128, blank=True)
    response_json = models.JSONField(default=dict, blank=True)
    response_code = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(
        choices=PaymentStatusType.choices, default=PaymentStatusType.pending
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                condition=models.Q(status=PaymentStatusType.pending),
                name="one_pending_payment_per_order",
            ),
            models.UniqueConstraint(
                fields=["gateway", "authority_id"],
                name="unique_gateway_authority",
            ),
        ]

    def __str__(self):
        return f"{self.gateway}:{self.authority_id}"
