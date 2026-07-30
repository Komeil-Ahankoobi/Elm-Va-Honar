from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class UsernameOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None

        user = None

        if username.isdigit() and username.startswith('09'):
            try:
                profile = Profile.objects.select_related('user').get(phone_number=username)
                user = profile.user
            except Profile.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None