from django.conf import settings
from django.db import models


class GatewayType(models.TextChoices):
    zarinpal = "zarinpal", "پرداخت با زرین‌پال"
    parsian = "parsian", "پرداخت با بانک پارسیان"


def parsian_available_for(user):
    """
    پارسیان فقط وقتی نمایش داده می‌شود که:
    - PARSIAN_ENABLED روشن باشد،
    - PARSIAN_LOGIN_ACCOUNT تنظیم شده باشد،
    - و اگر PARSIAN_STAFF_ONLY روشن است، کاربر staff باشد (برای تست اولیه).
    """
    if not getattr(settings, "PARSIAN_ENABLED", False):
        return False
    if not getattr(settings, "PARSIAN_LOGIN_ACCOUNT", ""):
        return False
    if getattr(settings, "PARSIAN_STAFF_ONLY", False):
        return bool(user is not None and getattr(user, "is_staff", False))
    return True


def available_gateways(user):
    """لیست (value, label) درگاه‌هایی که این کاربر اجازه‌ی استفاده از آن‌ها را دارد."""
    gateways = [(GatewayType.zarinpal.value, GatewayType.zarinpal.label)]
    if parsian_available_for(user):
        gateways.append((GatewayType.parsian.value, GatewayType.parsian.label))
    return gateways
