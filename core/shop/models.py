from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.urls import reverse


from .colors import VISTA_ACRYLIC_COLORS


class ProductStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")
   
 
class ProductCategoryModel(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)
    image = models.ImageField(default="default/آبرنگ.webp", upload_to="categories/img/")
    popular = models.BooleanField(default=False)
    baner = models.BooleanField(default=False)
    baner_image =  models.ImageField(default="default/cat-abner-3.webp", upload_to="cat-baners/img/")
    h3_text = models.CharField(max_length=200, null=True, blank=True)
    p_text = models.CharField(max_length=150, null=True, blank=True)

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
    

    def get_absolute_url(self):
        return reverse('shop:show-product-view') + f'?category={self.slug}'


    def get_meta_title(self):
        return self.meta_title or self.title

    def get_meta_description(self):
        return self.meta_description or f"خرید {self.title} با بهترین قیمت از فروشگاه علم و هنر"


class ProductBrandModel(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)
    image = models.ImageField(default="default/faber-castell.webp", upload_to="brands/img/")


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

    def get_absolute_url(self):
        return reverse('shop:show-product-view') + f'?brand={self.slug}'

    def get_meta_title(self):
        return self.meta_title or self.title

    def get_meta_description(self):
        return self.meta_description or f"خرید {self.title} با بهترین قیمت از فروشگاه علم و هنر"


class ProductModel(models.Model):
    category = models.ManyToManyField(
        ProductCategoryModel,
        related_name='products'
    )
    brand = models.ForeignKey(
        ProductBrandModel,
        on_delete=models.PROTECT,
        related_name='products',
        null=True, 
        blank=True,
    )
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

    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    status = models.IntegerField(choices=ProductStatusType.choices, default=ProductStatusType.draft.value)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0, null=True, blank=True)
    discount_percent = models.IntegerField(default=0, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def sync_visibility_from_stock(self):
        if self.has_variants():
            return

        current_stock = self.stock or 0
        if current_stock <= 0 and self.status != ProductStatusType.draft.value:
            self.status = ProductStatusType.draft.value
            self.save(update_fields=["status"])
        elif current_stock > 0 and self.status == ProductStatusType.draft.value:
            self.status = ProductStatusType.publish.value
            self.save(update_fields=["status"])

    def sync_parent_visibility_from_variants(self):
        if not self.has_variants():
            return

        total_stock = sum(v.stock for v in self.varients.all())
        if total_stock <= 0 and self.status != ProductStatusType.draft.value:
            self.status = ProductStatusType.draft.value
            self.save(update_fields=["status"])
        elif total_stock > 0 and self.status == ProductStatusType.draft.value:
            self.status = ProductStatusType.publish.value
            self.save(update_fields=["status"])
    

    def get_absolute_url(self):
        return reverse('shop:show-product-detail-view', kwargs={'slug': self.slug})

    def get_price_rial(self):
        return self.get_price() * 10

    def get_real_price(self):
        return self.price

    def __str__(self):
        return self.title

    def get_visible_variants(self):
        return self.varients.filter(status=ProductStatusType.publish.value)

    def get_price(self):
        if self.has_variants():
            prices = [v.get_price() for v in self.varients.all()]
            return min(prices) if prices else 0
        discount_amount = self.price * Decimal(self.discount_percent) / Decimal(100)
        discounted_amount = self.price - discount_amount
        return round(discounted_amount)

    def get_stock(self):
        if self.has_variants():
            return sum(v.stock for v in self.varients.all())
        return self.stock
    

    def is_publish(self):
        return self.status == ProductStatusType.publish.value

    def get_meta_title(self):
        return self.meta_title or f"{self.title} | خرید آنلاین - علم و هنر"

    def get_meta_description(self):
        return self.meta_description or (self.brief_description[:155] if self.brief_description else f"خرید {self.title} با بهترین قیمت و ارسال سریع از فروشگاه علم و هنر")

    def get_image_alt(self):
        return self.image_alt_text or self.title

    def get_color_variants(self):
        return self.varients.filter(variant_type=VarientType.color)

    def has_color_variants(self):
        return self.varients.filter(variant_type=VarientType.color).exists()

    def get_number_variants(self):
        return self.varients.filter(variant_type=VarientType.number)

    def has_number_variants(self):
        return self.varients.filter(variant_type=VarientType.number).exists()

    def has_variants(self):
        return self.varients.exists()

    def has_discount(self):
        if self.has_variants():
            return any(v.discount_percent > 0 for v in self.get_visible_variants())
        return bool(self.discount_percent and self.discount_percent > 0)

    def get_discount_percent(self):
        if self.has_variants():
            percents = [v.discount_percent for v in self.get_visible_variants() if v.discount_percent > 0]
            return max(percents) if percents else 0
        return self.discount_percent or 0

    def get_original_price_range(self):
        variants = list(self.get_visible_variants())
        if not variants:
            return None
        prices = [v.price for v in variants]
        return min(prices), max(prices)

    def get_price_range(self):
        variants = list(self.varients.all())
        if not variants:
            return None
        prices = [v.get_price() for v in variants]
        return min(prices), max(prices)
    
    
class ProductImageModel(models.Model):
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE, related_name="product_images")
    file = models.ImageField(upload_to="product/extra-img/")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["created_date"]
        
        
class VarientType(models.TextChoices):
    color = 'color', ("رنگ")
    number = 'number', ('شماره')


class ProductVarientModel(models.Model):
    product = models.ForeignKey(
        ProductModel, on_delete=models.CASCADE, related_name='varients'
    )
    variant_type = models.CharField(
        max_length=20, choices=VarientType.choices,
        help_text="نوع تنوع: اگه رنگه 'رنگ' انتخاب کن، اگه شماره‌س (مثل قلمو) 'شماره' انتخاب کن"
    )
    color_code = models.CharField(max_length=3, blank=True, null=True)
    number_code = models.CharField(max_length=5, blank=True, null=True)

    price = models.DecimalField(
        max_digits=10, decimal_places=0,
        help_text="قیمت مخصوص همین سایز/رنگ"
    )
    stock = models.PositiveIntegerField(
        default=0,
        help_text="موجودی مخصوص همین سایز/رنگ"
    )
    discount_percent = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="درصد تخفیف مخصوص همین سایز/رنگ"
    )
    status = models.IntegerField(
        choices=ProductStatusType.choices, default=ProductStatusType.publish.value,
        help_text="نمایش یا عدم نمایش همین سایز/رنگ به صورت مجزا"
    )

    def sync_visibility_from_stock(self):
       
        current_stock = self.stock or 0
        if current_stock <= 0 and self.status != ProductStatusType.draft.value:
            self.status = ProductStatusType.draft.value
            self.save(update_fields=["status"])
        elif current_stock > 0 and self.status == ProductStatusType.draft.value:
            self.status = ProductStatusType.publish.value
            self.save(update_fields=["status"])

        self.product.sync_parent_visibility_from_variants()

    def __str__(self):
        return f'{self.product.title} - {self.variant_type}'

    def get_hex_color(self):
        code = (self.color_code or "").strip().lstrip("#")
        if code in VISTA_ACRYLIC_COLORS:
            return VISTA_ACRYLIC_COLORS[code][1]
        return code or "cccccc"

    def get_color_display_name(self):
        code = (self.color_code or "").strip()
        if code in VISTA_ACRYLIC_COLORS:
            return VISTA_ACRYLIC_COLORS[code][0]
        return code

    def get_price(self):
        discount_amount = self.price * Decimal(self.discount_percent) / Decimal(100)
        return round(self.price - discount_amount)

    def has_discount(self):
        return bool(self.discount_percent and self.discount_percent > 0)


    def is_publish(self):
        return self.status == ProductStatusType.publish.value