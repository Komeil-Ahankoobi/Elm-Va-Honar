from django.contrib import admin
from .models import Profile


class CustomProfileAdmin(admin.ModelAdmin):
    list_display = ("id","user", "first_name","last_name","phone_number")
    searching_fields = ("user","first_name","last_name","phone_number")

admin.site.register(Profile, CustomProfileAdmin)
