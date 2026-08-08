from django.contrib import admin

from .models import (
    NewsLetterModel,
    BlogModel,
    BlogCategoryModel,
)

# Register your models here.
class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ['phone_number',]

class BlogModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'title', 'reading_time', 'status', 'views']

class BlogCategoryModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']



admin.site.register(NewsLetterModel, NewsLetterAdmin)
admin.site.register(BlogModel, BlogModelAdmin)
admin.site.register(BlogCategoryModel, BlogCategoryModelAdmin)