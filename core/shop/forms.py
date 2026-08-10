from django import forms


class PriceIncreaseForm(forms.Form):
    percentage = forms.DecimalField(
        label="درصد افزایش قیمت",
        min_value=0.01,
        max_value=1000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'مثلاً 10'}),
        help_text="عدد درصد رو وارد کن (مثلاً برای ۱۰٪ عدد 10 رو بزن)"
    )
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)