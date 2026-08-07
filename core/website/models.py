from django.db import models

from accounts.validators import validate_iranian_cellphone_number
from shop.models import ProductModel

# Create your models here.
class NewsLetterModel(models.Model):
    phone_number = models.CharField(max_length=12, validators=[validate_iranian_cellphone_number])
    
    def __str__(self):
        return self.phone_number


class BlogStatusType(models.IntegerChoices):
    publish = 1, "نمایش"
    draft = 2, "پیش‌نویس"


class BlogCategoryModel(models.Model):
    title = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True
    )

    meta_title = models.CharField(
        max_length=70,
        blank=True
    )

    meta_description = models.CharField(
        max_length=160,
        blank=True
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )

    updated_date = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.title


class BlogModel(models.Model):

    category = models.ForeignKey(
        BlogCategoryModel,
        on_delete=models.PROTECT,
        related_name="blogs"
    )

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True
    )

    image = models.ImageField(
        upload_to="blog/images/",
        default="default/default.png"
    )

    image_alt_text = models.CharField(
        max_length=255,
        blank=True
    )

    brief_description = models.TextField(
        blank=True,
        null=True
    )

    content = models.TextField()

    reading_time = models.PositiveIntegerField(default=1)

    related_products = models.ManyToManyField(
        ProductModel,
        blank=True,
        related_name="related_blogs"
    )

    status = models.IntegerField(
        choices=BlogStatusType.choices, 
        default=BlogStatusType.draft
    )

    views = models.PositiveIntegerField(default=0)

    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.title