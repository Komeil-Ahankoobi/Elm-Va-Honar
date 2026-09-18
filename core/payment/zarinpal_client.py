import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SUCCESS_CODES = (100, 101)


class ZarinPalClient:
    _timeout = 10

    def __init__(self, merchant_id=None, callback_url=None, sandbox=None, currency=None):
        self.merchant_id = merchant_id or settings.ZARINPAL_MERCHANT_ID
        self.callback_url = callback_url
        self.sandbox = (
            getattr(settings, "ZARINPAL_SANDBOX", False) if sandbox is None else sandbox
        )
        self.currency = currency or getattr(settings, "ZARINPAL_CURRENCY", "IRR")

        base = "https://sandbox.zarinpal.com" if self.sandbox else "https://payment.zarinpal.com"
        self.request_url = f"{base}/pg/v4/payment/request.json"
        self.verify_url = f"{base}/pg/v4/payment/verify.json"
        self.start_pay_url = f"{base}/pg/StartPay/"

    def payment_request(
        self,
        amount,
        description="پرداخت سفارش",
        *,
        mobile=None,
        email=None,
        order_id=None,
    ):
        if not self.callback_url:
            raise ValueError(
                "callback_url مشخص نشده. موقع ساخت ZarinPalClient باید callback_url پاس بدی."
            )

        payload = {
            "merchant_id": self.merchant_id,
            "amount": int(amount),
            "currency": self.currency,
            "description": description,
            "callback_url": self.callback_url,
        }

        metadata = {}
        if mobile:
            metadata["mobile"] = str(mobile)
        if email:
            metadata["email"] = str(email)
        if order_id is not None:
            metadata["order_id"] = str(order_id)
        if metadata:
            payload["metadata"] = metadata

        return self._post(self.request_url, payload, label="payment_request")

    def payment_verify(self, amount, authority):
        payload = {
            "merchant_id": self.merchant_id,
            "amount": int(amount),
            "authority": authority,
        }
        return self._post(self.verify_url, payload, label="payment_verify")


    def generate_payment_url(self, authority):
        return self.start_pay_url + authority

    def _post(self, url, payload, label=""):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=self._timeout
            )
        except requests.exceptions.Timeout:
            logger.error("ZarinPal %s timeout", label)
            return self._failure("timeout")
        except requests.exceptions.RequestException as e:
            logger.error("ZarinPal %s failed: %s", label, e)
            return self._failure("connection_error")

        try:
            body = response.json()
        except ValueError:
            logger.error(
                "ZarinPal %s returned non-JSON response (http=%s)",
                label,
                response.status_code,
            )
            return self._failure("invalid_response")

        result = self._normalize(body)
        if not result["ok"]:
            logger.warning(
                "ZarinPal %s unsuccessful: code=%s message=%s",
                label,
                result["code"],
                result["message"],
            )
        return result

    @staticmethod
    def _normalize(body):
        data = body.get("data")
        if not isinstance(data, dict):
            data = {}

        errors = body.get("errors")
        if isinstance(errors, list):
            errors = errors[0] if errors else {}
        if not isinstance(errors, dict):
            errors = {}

        code = data.get("code", errors.get("code"))

        return {
            "ok": code in SUCCESS_CODES,
            "code": code,
            "message": data.get("message") or errors.get("message"),
            "authority": data.get("authority"),
            "ref_id": data.get("ref_id"),
            "card_pan": data.get("card_pan"),
            "card_hash": data.get("card_hash"),
            "fee": data.get("fee"),
            "fee_type": data.get("fee_type"),
            "raw": body,
        }

    @staticmethod
    def _failure(reason):
        return {
            "ok": False,
            "code": None,
            "message": reason,
            "authority": None,
            "ref_id": None,
            "card_pan": None,
            "card_hash": None,
            "fee": None,
            "fee_type": None,
            "raw": {"error": reason},
        }