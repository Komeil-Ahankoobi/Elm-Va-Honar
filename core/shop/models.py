from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings


class ProductStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")
    
class ProductCategoryModel(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)

    meta_title = models.CharField(max_length=70, blank=True,
        help_text="اگه خالی بمونه از title استفاده می‌شه. حداکثر ۶۰-۷۰ کاراکتر.")
    meta_description = models.CharField(max_length=160, blank=True,
        help_text="توضیح کوتاه برای نتایج گوگل. حداکثر ۱۵۵-۱۶۰ کاراکتر.")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.title

    def get_meta_title(self):
        return self.meta_title or self.title

    def get_meta_description(self):
        return self.meta_description or f"خرید {self.title} با بهترین قیمت از فروشگاه علم و هنر"


class ProductModel(models.Model):
    category = models.ManyToManyField(ProductCategoryModel)
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)
    
    image = models.ImageField(default="default/default.png", upload_to="product/img/")
    image_alt_text = models.CharField(
        max_length=255, blank=True,
        help_text="متن جایگزین تصویر برای سئو. مثلاً: خرید بوم نقاشی سایز A3"
    )
    
    description = models.TextField()
    brief_description = models.TextField(null=True, blank=True)

    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    stock = models.PositiveIntegerField(default=0)
    status = models.IntegerField(choices=ProductStatusType.choices, default=ProductStatusType.draft.value)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    discount_percent = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    avg_rate = models.FloatField(default=0.0)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def get_price_rial(self):
        return self.get_price() * 10

    def __str__(self):
        return self.title

    def get_price(self):
        discount_amount = self.price * Decimal(self.discount_percent) / Decimal(100)
        discounted_amount = self.price - discount_amount
        return round(discounted_amount)

    def is_publish(self):
        return self.status == ProductStatusType.publish.value

    def get_meta_title(self):
        return self.meta_title or f"{self.title} | خرید آنلاین - علم و هنر"

    def get_meta_description(self):
        return self.meta_description or (self.brief_description[:155] if self.brief_description else f"خرید {self.title} با بهترین قیمت و ارسال سریع از فروشگاه علم و هنر")

    def get_image_alt(self):
        return self.image_alt_text or self.title
    
class ProductImageModel(models.Model):
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE, related_name="product_images")
    file = models.ImageField(upload_to="product/extra-img/")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        
        
class VarientType(models.TextChoices):
    color = 'color', ("رنگ")
    number = 'number', ('شماره')


class ProductVarientModel(models.Model):
    product = models.ForeignKey(
        ProductModel, on_delete=models.CASCADE, related_name='varients'
    )
    varient_type = models.CharField(
        max_length=20, choices=VarientType.choices,
        help_text="نوع تنوع: اگه رنگه 'رنگ' انتخاب کن، اگه شماره‌س (مثل قلمو) 'شماره' انتخاب کن"
    )
    color_code = models.CharField(
        max_length=3, blank=True, null=True,
        help_text="فقط برای نوع 'رنگ' پر کن. کد هگز، مثلاً 12"
    )
    number_code = models.CharField(
        max_length=5, blank=True, null=True,
        help_text="مثل 0000 یا 000 یا 00 یا 0 یا اعداد طبیعی مثل 16 و 15"
    )
    
    
    def __str__(self):
        return f'{self.product.title} - {self.varient_type}'