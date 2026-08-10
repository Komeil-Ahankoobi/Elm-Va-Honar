from decimal import Decimal
from django.contrib import admin, messages
from django.shortcuts import render
from .models import (
    ProductModel, 
    ProductImageModel, 
    ProductCategoryModel,
    ProductVarientModel,
    ProductBrandModel,
)
from .forms import PriceIncreaseForm


class ProductVarientInline(admin.TabularInline):
    model = ProductVarientModel
    extra = 0
    fields = ['variant_type', 'color_code', 'number_code', 'price']


@admin.action(description='افزایش درصدی قیمت محصولات انتخاب‌شده')
def increase_price_custom(modeladmin, request, queryset):
    form = None

    if 'apply' in request.POST:
        form = PriceIncreaseForm(request.POST)
        if form.is_valid():
            percentage = form.cleaned_data['percentage']
            multiplier = Decimal('1') + (percentage / Decimal('100'))

            updated_count = 0
            for product in queryset:
                product.price = product.price * multiplier
                product.save()
                updated_count += 1

            modeladmin.message_user(
                request,
                f'{updated_count} محصول با موفقیت {percentage}٪ افزایش قیمت پیدا کردن.',
                messages.SUCCESS
            )
            return None

    if not form:
        form = PriceIncreaseForm(
            initial={'_selected_action': queryset.values_list('id', flat=True)}
        )

    return render(
        request,
        'admin/increase_price.html',
        context={
            'products': queryset,
            'form': form,
            'title': 'افزایش درصدی قیمت',
        }
    )


@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "stock", "status", "price", "image_alt_text", "meta_title", "meta_description")
    list_filter = ("status", "category", "brand")
    search_fields = ("title", "meta_title")
    inlines = [ProductVarientInline]
    actions = [increase_price_custom]


@admin.register(ProductCategoryModel)
class ProductCategoryModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_date", "meta_title", "meta_description")
    search_fields = ("title",)


@admin.register(ProductBrandModel)
class ProductBrandModelModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_date", "meta_title", "meta_description")
    search_fields = ("title",)


@admin.register(ProductImageModel)
class ProductImageModelAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "created_date")