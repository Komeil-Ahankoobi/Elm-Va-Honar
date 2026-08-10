# accounts/services.py
import logging
import random
import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from .models import OTPCode

logger = logging.getLogger(__name__)


class OTPSendError(Exception):
    """Raised when the SMS provider fails or returns an error status."""
    pass


def generate_otp_code(length=5):
    return str(random.randint(10**(length - 1), (10**length) - 1))


def send_otp_sms(phone_number, code):
    """
    Sends the OTP through Kavenegar's Lookup (verify) endpoint.
    Raises OTPSendError on any network/API failure so the caller can
    show a proper error instead of silently pretending the SMS went out.
    """
    url = f"https://api.kavenegar.com/v1/{settings.KAVENEGAR_API_KEY}/verify/lookup.json"
    params = {"receptor": phone_number, "token": code, "template": "otpcode"}

    try:
        response = requests.post(url, data=params, timeout=5)
    except requests.RequestException as exc:
        logger.error("Kavenegar request failed for %s: %s", phone_number, exc)
        raise OTPSendError("ارتباط با سرویس پیامک برقرار نشد.") from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.error("Kavenegar returned non-JSON response (status %s) for %s", response.status_code, phone_number)
        raise OTPSendError("پاسخ نامعتبر از سرویس پیامک دریافت شد.") from exc

    return_status = data.get("return", {}).get("status")
    if response.status_code != 200 or return_status != 200:
        logger.error("Kavenegar error for %s: %s", phone_number, data)
        raise OTPSendError(data.get("return", {}).get("message", "ارسال پیامک با خطا مواجه شد."))

    logger.info("OTP sent to %s (status %s)", phone_number, return_status)
    return data


def can_request_otp(phone_number):
    """Cooldown between two consecutive OTP requests for the same number."""
    last_otp = OTPCode.objects.filter(phone_number=phone_number).order_by('-created_at').first()
    if last_otp and timezone.now() < last_otp.created_at + timedelta(seconds=120):
        return False
    return True


def check_daily_otp_limit(phone_number, max_requests=5, window_hours=24):
    """
    Hard cap on how many OTPs a single phone number can receive per day,
    independent of IP. This is what stops someone who rotates IPs (VPN/proxy)
    from still being able to drain SMS credit against one victim number,
    since the 120s cooldown alone would still allow ~700 sends/day.
    """
    since = timezone.now() - timedelta(hours=window_hours)
    count = OTPCode.objects.filter(phone_number=phone_number, created_at__gte=since).count()
    return count < max_requests


def get_client_ip(request):
    """
    Returns the real client IP, accounting for the fact that this app sits
    behind a proxy (Runflare) that terminates TLS and forwards over HTTP.
    Without this, REMOTE_ADDR is the proxy's IP for every visitor, which
    makes the IP rate limit either useless or lock out everyone at once.

    NOTE: this trusts X-Forwarded-For as-is. That's fine when there is a
    single trusted proxy in front of Django (the normal PaaS setup), but if
    you ever sit behind multiple/untrusted proxies, use a package like
    django-ipware instead, since a client can otherwise spoof this header.
    """
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        # The header can be a comma-separated chain; the first entry is
        # the original client as set by the nearest trusted proxy.
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def check_ip_rate_limit(request, max_requests=5, window_seconds=3600):
    ip = get_client_ip(request)
    key = f'otp_ip_{ip}'
    count = cache.get(key, 0)
    if count >= max_requests:
        return False
    cache.set(key, count + 1, window_seconds)
    return True