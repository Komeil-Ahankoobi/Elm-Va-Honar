from django.contrib import admin
from .models import (
    ProductModel, 
    ProductImageModel, 
    ProductCategoryModel,
    ProductVarientModel,
)


    
class ProductVarientInline(admin.TabularInline):
    model = ProductVarientModel
    extra = 0
    fields = ['variant_type', 'color_code', 'number_code']


@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "stock", "status","price", "image_alt_text", "meta_title", "meta_description")
    inlines = [ProductVarientInline]

@admin.register(ProductCategoryModel)
class ProductCategoryModelAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_date", "meta_title", "meta_description")

@admin.register(ProductImageModel)
class ProductImageModelAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "created_date")
    
