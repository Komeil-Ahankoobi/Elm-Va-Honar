from django.contrib import admin
from django.contrib.sessions.models import Session

from .models import Profile


class CustomProfileAdmin(admin.ModelAdmin):
    list_display = ("id","user", "first_name","last_name","phone_number")
    searching_fields = ("user","first_name","last_name","phone_number")
    

class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']
    randomly_fields = ['_session_data']

admin.site.register(Profile, CustomProfileAdmin)
admin.site.register(Session, SessionAdmin)

