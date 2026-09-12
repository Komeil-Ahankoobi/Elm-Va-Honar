# accounts/services.py
import logging
import secrets
from melipayamak import Api
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
    return str(secrets.randbelow(9 * 10 ** (length - 1)) + 10 ** (length - 1))


def send_otp_sms(phone_number, code):
    """
    Sends the OTP through Melipayamak's pattern-based ("bodyId") send
    endpoint (SendByBaseNumber).

    NOTE: our current sender line (MELIPAYAMAK_SENDER_NUMBER) is a public/
    shared line (خط خدماتی عمومی). Public lines are NOT allowed to send
    free-text SMS (the old `sms.send(...)` call used to return
    RetStatus 9 / "PublicNumber" for exactly this reason) - by regulation
    they can only send messages through an approved pattern.

    To use this you must first create an OTP pattern in the Melipayamak
    panel (پنل > پترن‌ها), get it approved, and put its id in
    settings.MELIPAYAMAK_BODY_ID (via env). Once you switch to a dedicated
    line that supports free-text sending, you can go back to
    `sms.send(phone_number, settings.MELIPAYAMAK_SENDER_NUMBER, text)`.

    Raises OTPSendError on any network/API failure so the caller can
    show a proper error instead of silently pretending the SMS went out.
    """
    api = Api(settings.MELIPAYAMAK_USERNAME, settings.MELIPAYAMAK_PASSWORD)
    sms = api.sms()

    try:
        # `code` here is passed as the pattern's variable value. If your
        # approved pattern has more than one placeholder, Melipayamak
        # expects the values separated by ";" in the order the
        # placeholders appear in the pattern, e.g. f"{name};{code}".
        response = sms.send_by_base_number(
            code, phone_number, settings.MELIPAYAMAK_BODY_ID
        )
    except Exception as exc:
        logger.error("Melipayamak request failed for %s: %s", phone_number, exc)
        raise OTPSendError("ارتباط با سرویس پیامک برقرار نشد.") from exc

    if not isinstance(response, dict):
        logger.error(
            "Melipayamak returned unexpected response type for %s: %r",
            phone_number,
            response,
        )
        raise OTPSendError("پاسخ نامعتبر از سرویس پیامک دریافت شد.")

    ret_status = response.get("RetStatus")
    if ret_status != 1:
        logger.error("Melipayamak error for %s: %s", phone_number, response)
        raise OTPSendError(response.get("StrRetStatus", "ارسال پیامک با خطا مواجه شد."))

    logger.info("OTP sent to %s (RecId %s)", phone_number, response.get("Value"))
    return response


def can_request_otp(phone_number):
    """Cooldown between two consecutive OTP requests for the same number."""
    last_otp = (
        OTPCode.objects.filter(phone_number=phone_number)
        .order_by("-created_at")
        .first()
    )
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
    count = OTPCode.objects.filter(
        phone_number=phone_number, created_at__gte=since
    ).count()
    return count < max_requests


MAX_OTP_ATTEMPTS = 5


def get_otp_attempt_key(phone_number):
    return f"otp_attempts_{phone_number}"


def register_failed_otp_attempt(phone_number):
    """
    هر تلاش ناموفق رو می‌شماره. وقتی به سقف رسید True برمی‌گردونه
    تا caller بتونه OTP رو باطل کنه.
    """
    key = get_otp_attempt_key(phone_number)
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, 300)
    return attempts >= MAX_OTP_ATTEMPTS


def reset_otp_attempts(phone_number):
    cache.delete(get_otp_attempt_key(phone_number))


def otp_attempts_exceeded(phone_number):
    return cache.get(get_otp_attempt_key(phone_number), 0) >= MAX_OTP_ATTEMPTS


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
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        # The header can be a comma-separated chain; the first entry is
        # the original client as set by the nearest trusted proxy.
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def check_ip_rate_limit(request, max_requests=5, window_seconds=3600):
    ip = get_client_ip(request)
    key = f"otp_ip_{ip}"
    count = cache.get(key, 0)
    if count >= max_requests:
        return False
    cache.set(key, count + 1, window_seconds)
    return True