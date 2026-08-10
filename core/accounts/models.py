from datetime import timedelta
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from django.db import models
from accounts.validators import validate_iranian_cellphone_number
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=12, unique=True, validators=[validate_iranian_cellphone_number])
    image = models.ImageField(upload_to="profile/", default="profile/default.png")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def get_fullname(self):
        if self.first_name or self.last_name:
            return self.first_name + " " + self.last_name
        return "کاربر جدید"

    def get_first_word_of_name(self):
        return self.first_name[0:1]


class OTPCode(models.Model):
    phone_number = models.CharField(max_length=12, db_index=True)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=2)

    def __str__(self):
        return f"{self.phone_number} - {self.code}"