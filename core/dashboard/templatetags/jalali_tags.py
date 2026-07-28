from django import template

from ..jalali_utils import (
    format_jalali_date,
    format_jalali_time,
    format_jalali_datetime,
)

register = template.Library()


@register.filter(name='jalali_date')
def jalali_date(value):
    """{{ order.created_date|jalali_date }} -> 1405/05/06"""
    return format_jalali_date(value)


@register.filter(name='jalali_time')
def jalali_time(value):
    """{{ order.created_date|jalali_time }} -> 10:45"""
    return format_jalali_time(value)


@register.filter(name='jalali_datetime')
def jalali_datetime(value):
    """{{ order.created_date|jalali_datetime }} -> 1405/05/06 - 10:45"""
    return format_jalali_datetime(value)