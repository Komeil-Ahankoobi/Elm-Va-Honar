from django import forms 
from django.utils import timezone

from .models import (
    UserAddressModel,
    CoponModel
)

class OrderCheckoutForm(forms.Form):
    address_id = forms.IntegerField(required=True)
    copon = forms.CharField(required=False)
    
    def __init__(self, *args, **kwargs):    
        self.request = kwargs.pop('request', None)
        super(OrderCheckoutForm, self).__init__(*args, **kwargs)

    
    def clean_address_id(self):
        address_id = self.cleaned_data.get('address_id')
        user = self.request.user

        try:
            address = UserAddressModel.objects.get(user=user, id=address_id)
        except UserAddressModel.DoesNotExist:
            raise forms.ValidationError('آدرس شما در پنل کاربریتون ثبت نشده است')

        return address
    
    
    def clean_copon(self):
        code = self.cleaned_data.get('copon')
        
        if code == '':
            return None

        user = self.request.user
        copon = None
        try:
            copon = CoponModel.objects.get(code=code)
        except CoponModel.DoesNotExist:
            raise forms.ValidationError('کد تخفیف اشتباه هست')

        if copon:
            
            if copon.is_usage_limit_reached:
                raise forms.ValidationError('میزان استفاده از کد به پایان رسیده است')
            
            if copon.expiration_date and copon.expiration_date < timezone.now():
                raise forms.ValidationError("کد تخفیف منقضی شده است")            

            if copon.is_used_by(user):
                raise forms.ValidationError("این کد قبلا توسط شما استفاده شده است")
            
        return copon