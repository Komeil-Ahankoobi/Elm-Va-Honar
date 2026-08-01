from django import forms 

from .models import NewsLetterModel

class NewsLetterForm(forms.ModelForm):
    class Meta:
        model = NewsLetterModel
        fields = ['phone_number']