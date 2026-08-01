from django.contrib import admin

from .models import NewsLetterModel

# Register your models here.
class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ['phone_number',]

admin.site.register(NewsLetterModel, NewsLetterAdmin)