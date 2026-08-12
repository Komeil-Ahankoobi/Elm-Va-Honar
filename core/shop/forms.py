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


class PriceDecreaseForm(forms.Form):
    percentage = forms.DecimalField(
        label="درصد کاهش قیمت",
        min_value=0.01,
        max_value=100,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'مثلاً 10'}),
        help_text="عدد درصد رو وارد کن (مثلاً برای ۱۰٪ کاهش عدد 10 رو بزن). حداکثر 100."
    )
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)


class DiscountPercentForm(forms.Form):
    discount_percent = forms.IntegerField(
        label="درصد تخفیف",
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'placeholder': 'مثلاً 10 یا برای حذف تخفیف 0'}),
        help_text="عدد بین ۰ تا ۱۰۰. برای حذف تخفیف عدد 0 رو بزن."
    )
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)