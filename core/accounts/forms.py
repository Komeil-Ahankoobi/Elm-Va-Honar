from django import forms
from .models import Profile
from .validators import validate_iranian_cellphone_number


class RegisterPhoneForm(forms.Form):
    first_name = forms.CharField(max_length=255, error_messages={'required': 'لطفاً نام را وارد کنید.'})
    last_name = forms.CharField(max_length=255, error_messages={'required': 'لطفاً نام خانوادگی را وارد کنید.'})
    phone_number = forms.CharField(
        max_length=12,
        validators=[validate_iranian_cellphone_number],
        error_messages={'required': 'لطفاً شماره تلفن را وارد کنید.'}
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("این شماره تلفن قبلا ثبت‌نام کرده است.")
        return phone_number


class LoginPhoneForm(forms.Form):
    phone_number = forms.CharField(
        max_length=12,
        validators=[validate_iranian_cellphone_number],
        error_messages={'required': 'لطفاً شماره تلفن را وارد کنید.'}
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not Profile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("کاربری با این شماره تلفن یافت نشد.")
        return phone_number


class VerifyOTPForm(forms.Form):
    code = forms.CharField(max_length=6, error_messages={'required': 'لطفاً کد را وارد کنید.'})