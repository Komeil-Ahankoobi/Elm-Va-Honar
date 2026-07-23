from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from django import forms

from shop.models import ProductModel

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
        

class AdminProductDetailEditFrom(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].widget.attrs.update({
    'class': 'action-btn',
    'style': 'width: 100%; padding: 0.75rem 1rem; text-align: right; cursor: text;'
})

        self.fields["title"].widget.attrs.update({
    'class': 'form-input text-right',
})

        self.fields["slug"].widget.attrs.update({
            'class': 'form-input text-right',
        })

        self.fields["image"].widget.attrs.update({
            'class': 'form-input',
        })

        self.fields["category"].widget.attrs.update({
            'class': 'form-input',
        })

        self.fields["price"].widget.attrs.update({
            'class': 'form-input text-center ltr',
        })

        self.fields["discount_percent"].widget.attrs.update({
            'class': 'form-input text-center ltr',
        })

        self.fields["stock"].widget.attrs.update({
            'class': 'form-input text-center ltr',
        })

        self.fields["status"].widget.attrs.update({
            'class': 'form-input text-center',
        })

        self.fields["description"].widget.attrs.update({
            'class': 'form-input',
        })
            
    class Meta:
        model = ProductModel
        fields = [
            'category',
            'title',
            'slug',
            'image',
            'description',
            'stock',
            'status',
            'price',
            'discount_percent',
        ]
        
