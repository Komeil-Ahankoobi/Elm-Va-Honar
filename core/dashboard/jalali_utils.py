import datetime

from django.utils import timezone

PERSIAN_MONTH_NAMES_FA = [
    'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
]


def _div(a, b):
    return a // b


def gregorian_to_jalali(gy, gm, gd):
    """تبدیل تاریخ میلادی به شمسی -> (jy, jm, jd)"""
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy + 1 if gm > 2 else gy
    days = (
        (365 * gy)
        + _div(gy2 + 3, 4)
        - _div(gy2 + 99, 100)
        + _div(gy2 + 399, 400)
        - 80
        + gd
        + g_d_m[gm - 1]
    )
    jy += 33 * _div(days, 12053)
    days %= 12053
    jy += 4 * _div(days, 1461)
    days %= 1461
    if days > 365:
        jy += _div(days - 1, 365)
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + _div(days, 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + _div(days - 186, 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd


def jalali_to_gregorian(jy, jm, jd):
    """تبدیل تاریخ شمسی به میلادی -> (gy, gm, gd)"""
    if jy > 979:
        gy = 1600
        jy -= 979
    else:
        gy = 621
    days = (
        (365 * jy)
        + (_div(jy, 33) * 8)
        + _div((jy % 33) + 3, 4)
        + 78
        + jd
        + ((31 * (jm - 1)) if jm < 7 else (((jm - 7) * 30) + 186))
    )
    gy += 400 * _div(days, 146097)
    days %= 146097
    if days > 36524:
        gy += 100 * _div(days - 1, 36524)
        days = (days - 1) % 36524
        if days >= 365:
            days += 1
    gy += 4 * _div(days, 1461)
    days %= 1461
    if days > 365:
        gy += _div(days - 1, 365)
        days = (days - 1) % 365
    gd = days + 1
    sal_a = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 366]
    leap = 1 if ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)) else 0
    gm = 0
    while gm < 13 and gd > (sal_a[gm] + (1 if gm == 1 and leap else 0)):
        gm += 1
    gd -= sal_a[gm - 1] + (1 if gm > 2 and leap else 0)
    return gy, gm, gd


def get_current_jalali_ymd():
    """تاریخ شمسی امروز را بر اساس زمان محلی برمی‌گرداند -> (jy, jm, jd)"""
    local_now = timezone.localtime(timezone.now())
    return gregorian_to_jalali(local_now.year, local_now.month, local_now.day)


def jalali_month_start_to_aware_gregorian(jy, jm):
    """اولین روز ماه شمسی (jy, jm) را به datetime آگاه میلادی تبدیل می‌کند"""
    gy, gm, gd = jalali_to_gregorian(jy, jm, 1)
    naive_dt = datetime.datetime(gy, gm, gd)
    if timezone.is_naive(naive_dt):
        naive_dt = timezone.make_aware(naive_dt)
    return naive_dt


def to_local(value):
    """اگر datetime آگاه باشد، به زمان محلی تبدیل می‌کند؛ در غیر این صورت همان مقدار را برمی‌گرداند"""
    if value and timezone.is_aware(value):
        return timezone.localtime(value)
    return value


def format_jalali_date(value):
    """خروجی مثل 1405/05/06"""
    local_dt = to_local(value)
    if not local_dt:
        return ''
    jy, jm, jd = gregorian_to_jalali(local_dt.year, local_dt.month, local_dt.day)
    return f'{jy:04d}/{jm:02d}/{jd:02d}'


def format_jalali_time(value):
    """خروجی مثل 10:45"""
    local_dt = to_local(value)
    if not local_dt:
        return ''
    return local_dt.strftime('%H:%M')


def format_jalali_datetime(value):
    """خروجی مثل 1405/05/06 - 10:45"""
    local_dt = to_local(value)
    if not local_dt:
        return ''
    return f'{format_jalali_time(local_dt)} - {format_jalali_date(local_dt)}'