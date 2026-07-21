from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _

class AdminPasswordChangeForm(PasswordChangeForm):
    error_messages = {
        "password_incorrect": _(
            "رمز قبلی شما اشتباه وارد شده است ، لطفا تصحیح فرمایید"
        ),
        "password_mismatch": _(
            "دو رمز ورودی با یکدیگر تطابق ندارند"
        )
    }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.fields["old_password"].widget.attrs['class'] = 'action-btn'        
        self.fields["old_password"].widget.attrs['placeholder'] = 'رمز فعلی خود را وارد نمایید'        
        
        self.fields["new_password1"].widget.attrs['class'] = 'action-btn'
        self.fields["new_password1"].widget.attrs['placeholder'] = 'رمز جدید خود را وارد نمایید'        


        self.fields["new_password2"].widget.attrs['class'] = 'action-btn'
        self.fields["new_password2"].widget.attrs['placeholder'] = 'تکرار رمز جدید'        