from django.contrib.auth import forms
from django.contrib.auth.forms import AuthenticationForm
from django import forms as main_form
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile  # مسیر واقعی مدل خودتون رو بذارید
from .validators import validate_iranian_cellphone_number  # مسیر واقعی validator


class UserRegisterForm(UserCreationForm):

    phone_number = main_form.CharField(
        max_length=12,
        validators=[validate_iranian_cellphone_number],
        error_messages={'required': 'لطفاً شماره تلفن را وارد کنید.'}
    )

    error_messages = {
        'password_mismatch': 'رمز عبور و تکرار آن یکسان نیستند.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].error_messages['required'] = 'لطفاً نام کاربری را وارد کنید.'
        self.fields['email'].error_messages['required'] = 'لطفاً ایمیل را وارد کنید.'
        self.fields['password1'].error_messages['required'] = 'لطفاً رمز عبور را وارد کنید.'
        self.fields['password2'].error_messages['required'] = 'لطفاً تکرار رمز عبور را وارد کنید.'
        self.fields['first_name'].error_messages['required'] = 'لطفاً نام را وارد کنید.'
        self.fields['last_name'].error_messages['required'] = 'لطفاً نام خانوادگی را وارد کنید.'

        self.fields['email'].error_messages['invalid'] = 'ایمیل وارد شده معتبر نیست.'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("این نام کاربری قبلا استفاده شده است .")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if Profile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("این شماره تلفن قبلا استفاده شده است.")
        return phone_number

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        
class UserLoginForm(AuthenticationForm):

    error_messages = {
        "invalid_login": "نام کاربری/شماره تلفن یا رمز عبور اشتباه است.",
        "inactive": "حساب کاربری شما غیرفعال است.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'نام کاربری یا شماره تلفن'
        self.fields['username'].error_messages['required'] = 'لطفاً نام کاربری یا شماره تلفن را وارد کنید.'
        self.fields['password'].error_messages['required'] = 'لطفاً رمز عبور را وارد کنید.'

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)