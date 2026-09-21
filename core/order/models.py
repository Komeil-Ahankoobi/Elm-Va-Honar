from django.db import models, transaction
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
from django.conf import settings

from shop.models import (
    ProductModel,
    ProductVarientModel,
)


class OrderStatusType(models.IntegerChoices):
    pending = 1, "در حال پرداخت"
    paid = 2, "پرداخت شده"
    processing = 3, "پردازش شده"
    preparing = 4, "در حال آماده‌سازی"
    shipped = 5, "تحویل پست مبدا داده شد"
    cancelled = 6, "لغو شده"


class UserAddressModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="adresses")

    address = models.CharField(max_length=255)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)


class CoponModel(models.Model):
    code = models.CharField(max_length=100, unique=True)
    discount_percent = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    max_limit_usage = models.PositiveIntegerField(default=10)
    used_by = models.ManyToManyField(User, related_name="copon_users", blank=True)

    expiration_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    @property
    def is_usage_limit_reached(self):
        return self.used_by.count() >= self.max_limit_usage

    def is_used_by(self, user):
        return user in self.used_by.all()

    def __str__(self):
        return self.code


class OrderModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    address = models.CharField(max_length=255)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)

    subtotal_price = models.DecimalField(
        default=0, max_digits=10, decimal_places=0
    )  # جمع کل قبل از تخفیفِ کد تخفیف
    total_price = models.DecimalField(
        default=0, max_digits=10, decimal_places=0
    )  # جمع نهایی بعد از تخفیفِ کد تخفیف (بدون مالیات)

    copon = models.ForeignKey(
        CoponModel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="copon",
    )
    # اسنپ‌شاتِ کد تخفیف در لحظه‌ی خرید (چون ممکنه copon بعداً حذف/ادیت بشه)
    copon_code = models.CharField(max_length=100, null=True, blank=True)
    copon_discount_percent = models.PositiveIntegerField(default=0)
    discount_amount = models.DecimalField(default=0, max_digits=10, decimal_places=0)

    status = models.IntegerField(
        choices=OrderStatusType.choices, default=OrderStatusType.pending.value
    )

    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["-created_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status=OrderStatusType.pending.value),
                name="one_pending_order_per_user",
            )
        ]

    PENDING_TIMEOUT_MINUTES = 15 


    @classmethod
    def expire_stale_pending(cls, user=None):
       
        cutoff = timezone.now() - timezone.timedelta(minutes=cls.PENDING_TIMEOUT_MINUTES)
        qs = cls.objects.filter(status=OrderStatusType.pending.value, created_date__lt=cutoff)
        if user is not None:
            qs = qs.filter(user=user)

        for order in qs:
            order.cancel_payment()

    @classmethod
    def get_active_pending_order(cls, user):
        return cls.objects.filter(
            user=user, status=OrderStatusType.pending.value
        ).first()



    def __str__(self):
        return f"{self.user.user_profile.get_fullname()} - {self.id}"

    def get_status(self):
        return {
            "id": self.status,
            "title": OrderStatusType(self.status).name,
            "label": OrderStatusType(self.status).label,
        }

    def calculate_total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())

    def get_total_items_quantity(self):
        result = self.items.aggregate(total=Sum("quantity"))
        return result["total"] or 0

    def get_tax_amount(self):
        return round(self.total_price * Decimal("10") / Decimal("100"))

    def get_total_price(self):
        return self.total_price + self.get_tax_amount()

    @property
    def has_copon(self):
        return bool(self.copon_code)

    @property
    def is_successful(self):
        """سفارش‌هایی که پرداخت‌شون موفقیت‌آمیز بوده (از مرحله پرداخت به بعد)"""
        return self.status in {
            OrderStatusType.paid.value,
            OrderStatusType.processing.value,
            OrderStatusType.preparing.value,
            OrderStatusType.shipped.value,
        }

    @property
    def is_cancellable(self):
        """فقط وقتی هنوز ارسال نهایی نشده باشه"""
        return self.status in {
            OrderStatusType.pending.value,
            OrderStatusType.paid.value,
            OrderStatusType.processing.value,
            OrderStatusType.preparing.value,
        }

    def confirm_payment(self):
        if self.is_successful:
            return

        with transaction.atomic():
            self._decrease_stock()

            self.status = OrderStatusType.paid.value
            self.save(update_fields=["status", "updated_date"])

            if self.copon:
                self.copon.used_by.add(self.user)

            from cart.models import CartModel

            cart = CartModel.objects.filter(user=self.user).first()
            if cart:
                cart.cart_items.all().delete()

    def cancel_payment(self):
        # سفارش را حذف نمی‌کنیم؛ سابقه‌ی سفارش باید برای کاربر و ادمین باقی بماند.
        # اگر قبلاً ارسال شده، دیگر اجازه‌ی لغو نمی‌دهیم.
        if self.status == OrderStatusType.shipped.value:
            return

        self.status = OrderStatusType.cancelled.value
        self.save(update_fields=["status", "updated_date"])

    def _decrease_stock(self):
        for item in self.items.select_related("product", "variant"):
            stock_obj = item.variant if item.variant else item.product
            model_class = type(stock_obj)

            locked_obj = model_class.objects.select_for_update().get(pk=stock_obj.pk)
            current_stock = locked_obj.stock or 0
            locked_obj.stock = max(current_stock - item.quantity, 0)
            locked_obj.save(update_fields=["stock"])
            locked_obj.sync_visibility_from_stock()

    # is_successful قبلاً به صورت property تعریف شد


class OrderItemsModel(models.Model):
    order = models.ForeignKey(
        OrderModel, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(ProductModel, on_delete=models.PROTECT)
    variant = models.ForeignKey(
        ProductVarientModel, on_delete=models.SET_NULL, null=True, blank=True
    )

    quantity = models.PositiveIntegerField(default=0)

    original_price = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    discount_percent = models.IntegerField(default=0)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)

    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)

    @property
    def has_discount(self):
        return bool(self.discount_percent and self.discount_percent > 0)

    @property
    def unit_price(self):
        return self.price

    @property
    def unit_discount_amount(self):
        if not self.has_discount:
            return 0
        return self.original_price - self.price

    @property
    def total_discount_amount(self):
        return self.unit_discount_amount * self.quantity

    @property
    def original_total_price(self):
        return self.original_price * self.quantity

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        variant_part = self.variant.variant_type if self.variant else "بدون وریانت"
        return f"{self.product.title} - {variant_part} - {self.order.id}"



class PostPrice(models.Model):
    price = models.PositiveIntegerField(default=190000, verbose_name="قیمت پست (تومان)")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"{self.price} تومان"