from django.contrib import admin

from .models import (
    NewsLetterModel,
    BlogModel,
    BlogCategoryModel,
    BlogKeyPointModel,
    BlogFAQModel
)

# Register your models here.
class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ['phone_number',]

class BlogModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'title', 'reading_time', 'status']

class BlogCategoryModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

class BlogKeyPointInline(admin.TabularInline):
    model = BlogKeyPointModel
    extra = 1

class BlogFAQInline(admin.TabularInline):
    model = BlogFAQModel
    extra = 1

@admin.register(BlogModel)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'title', 'reading_time', 'status']
    inlines = [BlogKeyPointInline, BlogFAQInline]
    filter_horizontal = ['related_products']

admin.site.register(NewsLetterModel, NewsLetterAdmin)   

admin.site.register(BlogCategoryModel, BlogCategoryModelAdmin)