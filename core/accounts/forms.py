from django.contrib.auth import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    
    error_messages = {
        'password_mismatch': 'رمز عبور و تکرار آن یکسان نیستند.',
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].error_messages['required'] = 'لطفاً نام کاربری را وارد کنید.'
        self.fields['email'].error_messages['required'] = 'لطفاً ایمیل را وارد کنید.'
        self.fields['password1'].error_messages['required'] = 'لطفاً رمز عبور را وارد کنید.'
        self.fields['password2'].error_messages['required'] = 'لطفاً تکرار رمز عبور را وارد کنید.'

        self.fields['email'].error_messages['invalid'] = 'ایمیل وارد شده معتبر نیست.'
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("این نام کاربری قبلا استفاده شده است .")
        return username
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
        
class UserLoginForm(forms.AuthenticationForm):
    
    error_messages = {
        "invalid_login": "نام کاربری یا رمز عبور اشتباه است.",
        "inactive": "حساب کاربری شما غیرفعال است.",
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages['required'] = 'لطفاً نام کاربری را وارد کنید.'
        self.fields['password'].error_messages['required'] = 'لطفاً رمز عبور را وارد کنید.'
    
    def confirm_login_allowed(self, user):
        super(UserLoginForm,self).confirm_login_allowed(user)