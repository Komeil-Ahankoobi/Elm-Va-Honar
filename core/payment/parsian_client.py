"""
کلاینت درگاه پارسیان (SOAP 1.1) بر اساس WSDLهای رسمی:
  Sale     : SalePaymentRequest   (ساخت Token)
  Confirm  : ConfirmPayment       (تأیید پرداخت)
  Reversal : ReversalRequest      (برگشت پرداخت)

بدون وابستگی اضافه (فقط requests که از قبل دارید).
همه‌ی متدها همیشه dict برمی‌گردانند و exception نمی‌دهند؛ خطای شبکه با ok=False و
code=None برمی‌گردد (یعنی «نامشخص»، نه «ناموفق»).
"""

import logging
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# namespace دقیقاً مطابق WSDL (حرف S بزرگ در Shaparak مهم است)
SALE_NS = "https://pec.Shaparak.ir/NewIPGServices/Sale/SaleService"
CONFIRM_NS = "https://pec.Shaparak.ir/NewIPGServices/Confirm/ConfirmService"
REVERSAL_NS = "https://pec.Shaparak.ir/NewIPGServices/Reversal/ReversalService"

SALE_URL = "https://pec.shaparak.ir/NewIPGServices/Sale/SaleService.asmx"
CONFIRM_URL = "https://pec.shaparak.ir/NewIPGServices/Confirm/ConfirmService.asmx"
REVERSAL_URL = "https://pec.shaparak.ir/NewIPGServices/Reverse/ReversalService.asmx"
PAY_URL = "https://pec.shaparak.ir/NewIPG/?Token="

# Status موفق در پاسخ سرویس‌ها (قابل تغییر از settings اگر بانک چیز دیگری گفت)
SUCCESS_STATUS = 0


def _int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _local(tag):
    return tag.rsplit("}", 1)[-1]


class ParsianClient:
    _timeout = (5, 15)  # (connect, read) ثانیه

    def __init__(self, login_account=None, callback_url=None):
        self.login_account = login_account or getattr(
            settings, "PARSIAN_LOGIN_ACCOUNT", ""
        )
        if not self.login_account:
            raise ValueError("PARSIAN_LOGIN_ACCOUNT تنظیم نشده است.")
        self.callback_url = callback_url
        self.success_status = getattr(settings, "PARSIAN_SUCCESS_STATUS", SUCCESS_STATUS)

    # ------------------------------------------------------------------ API
    def payment_request(self, amount_rial, order_id, additional_data=None):
        """ساخت Token. amount_rial باید «ریال» باشد."""
        if not self.callback_url:
            raise ValueError("callback_url مشخص نشده.")
        data = self._call(
            SALE_URL,
            SALE_NS,
            "SalePaymentRequest",
            [
                ("LoginAccount", self.login_account),
                ("Amount", int(amount_rial)),
                ("OrderId", int(order_id)),
                ("CallBackUrl", self.callback_url),
                ("AdditionalData", additional_data),
            ],
        )
        if data is None:
            return self._failure("request_failed")
        status = _int(data.get("Status"))
        token = _int(data.get("Token"))
        ok = status == self.success_status and bool(token and token > 0)
        if not ok:
            logger.warning(
                "Parsian payment_request unsuccessful: status=%s message=%s",
                status,
                data.get("Message"),
            )
        return {
            "ok": ok,
            "code": status,
            "message": data.get("Message"),
            "authority": str(token) if ok else None,
            "raw": data,
        }

    def payment_verify(self, token):
        """تأیید پرداخت (Confirm). اگر تأیید نشود، بانک خودش تراکنش را برمی‌گرداند."""
        data = self._call(
            CONFIRM_URL,
            CONFIRM_NS,
            "ConfirmPayment",
            [("LoginAccount", self.login_account), ("Token", int(token))],
        )
        if data is None:
            return self._failure("confirm_failed")
        status = _int(data.get("Status"))
        rrn = _int(data.get("RRN"))
        # مطابق نمونه‌کد رسمی پارسیان: موفقیت Confirm فقط با Status == 0 تعیین می‌شود.
        ok = status == self.success_status
        if not ok:
            logger.warning(
                "Parsian payment_verify unsuccessful: token=%s status=%s rrn=%s",
                token,
                status,
                rrn,
            )
        return {
            "ok": ok,
            "code": status,
            "message": None,
            "ref_id": rrn if rrn and rrn > 0 else None,
            "card_pan": data.get("CardNumberMasked") or "",
            "card_hash": "",
            "raw": data,
        }

    def payment_reversal(self, token):
        """برگشت تراکنش (پول به حساب کاربر برمی‌گردد)."""
        data = self._call(
            REVERSAL_URL,
            REVERSAL_NS,
            "ReversalRequest",
            [("LoginAccount", self.login_account), ("Token", int(token))],
        )
        if data is None:
            return self._failure("reversal_failed")
        status = _int(data.get("Status"))
        ok = status == self.success_status
        if not ok:
            logger.warning(
                "Parsian payment_reversal unsuccessful: token=%s status=%s message=%s",
                token,
                status,
                data.get("Message"),
            )
        return {
            "ok": ok,
            "code": status,
            "message": data.get("Message"),
            "raw": data,
        }

    @staticmethod
    def generate_payment_url(token):
        return PAY_URL + str(token)

    # ------------------------------------------------------------ internals
    @staticmethod
    def _envelope(ns, operation, fields):
        inner = "".join(
            f"<{name}>{escape(str(value))}</{name}>"
            for name, value in fields
            if value not in (None, "")
        )
        return (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
            f'<soap:Body><{operation} xmlns="{ns}">'
            f"<requestData>{inner}</requestData>"
            f"</{operation}></soap:Body></soap:Envelope>"
        )

    def _call(self, url, ns, operation, fields):
        """
        درخواست SOAP می‌زند و فیلدهای داخل <OperationResult> را به‌صورت dict برمی‌گرداند.
        در هر خطای شبکه/پاسخ نامعتبر None برمی‌گرداند (نه exception).
        """
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": f'"{ns}/{operation}"',
        }
        body = self._envelope(ns, operation, fields).encode("utf-8")
        try:
            response = requests.post(
                url, data=body, headers=headers, timeout=self._timeout
            )
        except requests.exceptions.Timeout:
            logger.error("Parsian %s timeout", operation)
            return None
        except requests.exceptions.RequestException as exc:
            logger.error("Parsian %s connection error: %s", operation, exc)
            return None

        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            logger.error(
                "Parsian %s returned non-XML response (http=%s)",
                operation,
                response.status_code,
            )
            return None

        result_tag = f"{operation}Result"
        for element in root.iter():
            if _local(element.tag) == result_tag:
                return {
                    _local(child.tag): (child.text or "").strip()
                    for child in element.iter()
                    if child is not element
                }

        logger.error(
            "Parsian %s: no %s in response (http=%s)",
            operation,
            result_tag,
            response.status_code,
        )
        return None

    @staticmethod
    def _failure(reason):
        return {
            "ok": False,
            "code": None,
            "message": reason,
            "authority": None,
            "ref_id": None,
            "card_pan": "",
            "card_hash": "",
            "raw": {"error": reason},
        }