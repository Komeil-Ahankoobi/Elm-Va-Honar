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
from .forms import PriceIncreaseForm, PriceDecreaseForm, DiscountPercentForm


class ProductVarientInline(admin.TabularInline):
    model = ProductVarientModel
    extra = 0
    fields = ['variant_type', 'color_code', 'number_code', 'price', 'stock', 'discount_percent', 'status']


class ProductImageInline(admin.TabularInline):
    model = ProductImageModel
    extra = 1
    fields = ['file']


@admin.action(description='افزایش درصدی قیمت موارد انتخاب‌شده')
def increase_price_custom(modeladmin, request, queryset):
    form = None

    if 'apply' in request.POST:
        form = PriceIncreaseForm(request.POST)
        if form.is_valid():
            percentage = form.cleaned_data['percentage']
            multiplier = Decimal('1') + (percentage / Decimal('100'))

            updated_count = queryset.count()
            for obj in queryset:
                obj.price = obj.price * multiplier
                obj.save()

            modeladmin.message_user(
                request,
                f'{updated_count} مورد با موفقیت {percentage}٪ افزایش قیمت پیدا کردن.',
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


@admin.action(description='کاهش درصدی قیمت موارد انتخاب‌شده')
def decrease_price_custom(modeladmin, request, queryset):
    form = None

    if 'apply' in request.POST:
        form = PriceDecreaseForm(request.POST)
        if form.is_valid():
            percentage = form.cleaned_data['percentage']
            multiplier = Decimal('1') - (percentage / Decimal('100'))

            updated_count = queryset.count()
            for obj in queryset:
                obj.price = obj.price * multiplier
                obj.save()

            modeladmin.message_user(
                request,
                f'{updated_count} مورد با موفقیت {percentage}٪ کاهش قیمت پیدا کردن.',
                messages.SUCCESS
            )
            return None

    if not form:
        form = PriceDecreaseForm(
            initial={'_selected_action': queryset.values_list('id', flat=True)}
        )

    return render(
        request,
        'admin/decrease_price.html',
        context={
            'products': queryset,
            'form': form,
            'title': 'کاهش درصدی قیمت',
        }
    )


@admin.action(description='تنظیم درصد تخفیف موارد انتخاب‌شده')
def set_discount_percent(modeladmin, request, queryset):
    form = None

    if 'apply' in request.POST:
        form = DiscountPercentForm(request.POST)
        if form.is_valid():
            discount_percent = form.cleaned_data['discount_percent']
            updated_count = queryset.update(discount_percent=discount_percent)

            modeladmin.message_user(
                request,
                f'تخفیف {updated_count} مورد روی {discount_percent}٪ تنظیم شد.',
                messages.SUCCESS
            )
            return None

    if not form:
        form = DiscountPercentForm(
            initial={'_selected_action': queryset.values_list('id', flat=True)}
        )

    return render(
        request,
        'admin/set_discount.html',
        context={
            'products': queryset,
            'form': form,
            'title': 'تنظیم درصد تخفیف',
        }
    )


@admin.action(description='حذف فوری تخفیف (صفر کردن بدون فرم)')
def remove_discount_instant(modeladmin, request, queryset):
    updated_count = queryset.update(discount_percent=0)
    modeladmin.message_user(
        request,
        f'تخفیف {updated_count} مورد صفر شد.',
        messages.SUCCESS
    )


@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "stock", "status", "price", "discount_percent", "image_alt_text", "meta_title", "meta_description")
    list_filter = ("status", "category", "brand")
    search_fields = ("title", "meta_title")
    inlines = [ProductVarientInline, ProductImageInline]
    actions = [increase_price_custom, decrease_price_custom, set_discount_percent, remove_discount_instant]


@admin.register(ProductVarientModel)
class ProductVarientModelAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "variant_type", "number_code", "color_code", "price", "stock", "discount_percent", "status")
    list_filter = ("variant_type", "status", "product__category")
    search_fields = ("product__title", "number_code", "color_code")
    actions = [increase_price_custom, decrease_price_custom, set_discount_percent, remove_discount_instant]


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