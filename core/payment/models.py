from django.db import models


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
    authority_id = models.CharField(max_length=255, unique=True, db_index=True)
    ref_id = models.BigIntegerField(null=True, blank=True)
    amount = models.PositiveBigIntegerField(default=0)
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
            )
        ]

    def __str__(self):
        return self.authority_id