from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.sessions.models import Session


from .models import Profile



class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fields = ("first_name", "last_name", "phone_number", "image")


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "id",
        "get_first_name",
        "get_last_name",
        "get_phone_number",
        "is_staff",
    )
    search_fields = (
        "user_profile__first_name",
        "user_profile__last_name",
        "user_profile__phone_number",
    )

    def get_first_name(self, obj):
        return obj.user_profile.first_name

    get_first_name.short_description = "نام"

    def get_last_name(self, obj):
        return obj.user_profile.last_name

    get_last_name.short_description = "نام خانوادگی"

    def get_phone_number(self, obj):
        return obj.user_profile.phone_number

    get_phone_number.short_description = "شماره تلفن"


class CustomProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "first_name", "last_name", "phone_number")
    search_fields = ("first_name", "last_name", "phone_number")


class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()

    list_display = ["session_key", "_session_data", "expire_date"]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, CustomProfileAdmin)
admin.site.register(Session, SessionAdmin)
