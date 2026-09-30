from django import forms
from django.utils.safestring import mark_safe
import jdatetime
from datetime import datetime


class JalaliDateTimeWidget(forms.DateTimeInput):
    """
    ویجت ورودی تاریخ و ساعت شمسی برای ادمین
    فرمت ورودی: 1403/06/27 14:30
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'placeholder': 'مثال: 1403/06/27 14:30',
            'class': 'vDateField',  # استایل ادمین جنگو
            'style': 'width: 180px;',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format='%Y/%m/%d %H:%M')

    def format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        # تبدیل میلادی به شمسی برای نمایش
        try:
            jalali = jdatetime.datetime.fromgregorian(datetime=value)
            return jalali.strftime('%Y/%m/%d %H:%M')
        except Exception:
            return super().format_value(value)


class JalaliDateTimeField(forms.DateTimeField):
    widget = JalaliDateTimeWidget

    def to_python(self, value):
        if value in self.empty_values:
            return None

        if isinstance(value, datetime):
            return value

        # ورودی شمسی رو به میلادی تبدیل می‌کنیم
        try:
            # فرمت‌های مختلف رو پشتیبانی می‌کنیم
            value = value.strip()
            for fmt in ('%Y/%m/%d %H:%M', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d'):
                try:
                    jalali_dt = jdatetime.datetime.strptime(value, fmt)
                    return jalali_dt.togregorian()
                except ValueError:
                    continue
            raise ValueError
        except (ValueError, TypeError):
            raise forms.ValidationError(
                'فرمت تاریخ نامعتبر است. مثال صحیح: 1403/06/27 14:30'
            )