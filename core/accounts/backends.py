from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Profile, OTPCode

User = get_user_model()


class PhoneOTPBackend(ModelBackend):
    def authenticate(self, request, phone_number=None, code=None, **kwargs):
        if not phone_number or not code:
            return None

        otp = OTPCode.objects.filter(
            phone_number=phone_number, is_used=False
        ).order_by('-created_at').first()

        if otp is None or otp.code != code or otp.is_expired():
            return None

        otp.is_used = True
        otp.save(update_fields=['is_used'])

        try:
            return Profile.objects.select_related('user').get(phone_number=phone_number).user
        except Profile.DoesNotExist:
            return None