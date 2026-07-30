from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

from shop.models import (
    ProductModel,
    ProductVarientModel,
)

# Create your models here.
class OrderStatusType(models.IntegerChoices):
    pending = 1, 'در انتظار پرداخت'
    succes = 2, 'پرداخت شده'
    faild = 3, 'لغو شده'
    complete = 4, 'ارسال شده'


class UserAddressModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adresses')
    
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    

class CoponModel(models.Model):
    code = models.CharField(max_length=100, unique=True)
    discount_percent = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_limit_usage = models.PositiveIntegerField(default=10)
    used_by = models.ManyToManyField(User, related_name='copon_users', blank=True)

    expiration_date = models.DateTimeField(null=True,blank=True)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    address = models.CharField(max_length=255)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=50)

    total_price = models.DecimalField(default=0, max_digits=10, decimal_places=0)

    copon = models.ForeignKey(CoponModel, on_delete=models.PROTECT, null=True, blank=True, related_name='copon')
    status = models.IntegerField(choices=OrderStatusType.choices, default=OrderStatusType.pending.value)

    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]
        
        
    def __str__(self):
        return f'{self.user.username} - {self.id}'
    
    def get_status(self):
        return {
            "id":self.status,
            "title":OrderStatusType(self.status).name,
            "label":OrderStatusType(self.status).label,
        }
        
    # def get_price(self):
    #     if self.copon:
    #         discount = Decimal(self.copon.discount_percent) / Decimal("100")
    #         return round(self.total_price - (self.total_price * discount))
    #     return self.total_price
    
    def calculate_total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())

    def get_total_items_quantity(self):
        result = self.items.aggregate(total=Sum("quantity"))
        return result["total"] or 0
    
    @property
    def get_discount_price(self):
        if not self.copon:
            return 0
        discount = Decimal(self.copon.discount_percent) / Decimal("100")
        return round(self.calculate_total_price() * discount)

    @property
    def is_successful(self):
        return self.status == OrderStatusType.succes.value


class OrderItemsModel(models.Model):
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductModel, on_delete=models.PROTECT)
    variant = models.ForeignKey(
        ProductVarientModel, on_delete=models.SET_NULL,
        null=True, blank=True
    )

    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)

    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)

    @property
    def unit_price(self):
        return self.price

    @property
    def total_price(self):
        return self.price * self.quantity


    def __str__(self):
        variant_part = self.variant.varient_type if self.variant else 'بدون وریانت'
        return f'{self.product.title} - {variant_part} - {self.order.id}'