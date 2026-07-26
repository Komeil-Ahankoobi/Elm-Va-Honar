from django import forms 
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from django import forms

from order.models import UserAddressModel

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddressModel
        fields = [
            "address",
            "state",
            "city",
            "zip_code",
        ]
        

class CustomerPasswordChangeForm(PasswordChangeForm):
    error_messages = {
        "password_incorrect": _(
            "رمز قبلی شما اشتباه وارد شده است ، لطفا تصحیح فرمایید"
        ),
        "password_mismatch": _(
            "دو رمز ورودی با یکدیگر تطابق ندارند"
        )
    }