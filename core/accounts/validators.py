from django.core.exceptions import ValidationError
import re

def validate_iranian_cellphone_number(value):
    pattern = r'^09\d{9}$'
    if not re.fullmatch(pattern, value):
        raise ValidationError('شماره موبایل معتبر نیست. مثال: 09123456789')