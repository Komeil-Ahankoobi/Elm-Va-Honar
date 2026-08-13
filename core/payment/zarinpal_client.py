import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ZarinPalSandbox:
    _payment_request_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
    _payment_verify_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
    _payment_page_url = "https://sandbox.zarinpal.com/pg/StartPay/"
    _timeout = 10

    def __init__(self, merchant_id=None, callback_url=None):
        self.merchant_id = merchant_id or settings.MERCHANT_ID
        self.callback_url = callback_url

    def payment_request(self, amount, description="پرداختی کاربر"):
        if not self.callback_url:
            raise ValueError(
                "callback_url مشخص نشده. موقع ساخت ZarinPalSandbox باید callback_url پاس بدی."
            )

        payload = {
            "MerchantID": self.merchant_id,
            "Amount": str(amount),
            "CallbackURL": self.callback_url,
            "Description": description,
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self._payment_request_url,
                headers=headers,
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.error("ZarinPal payment_request timeout")
            return {"Status": 0, "error": "timeout"}
        except requests.exceptions.RequestException as e:
            logger.error("ZarinPal payment_request failed: %s", e)
            return {"Status": 0, "error": "connection_error"}

        try:
            return response.json()
        except ValueError:
            logger.error("ZarinPal payment_request returned non-JSON response")
            return {"Status": 0, "error": "invalid_response"}

    def payment_verify(self, amount, authority):
        payload = {
            "MerchantID": self.merchant_id,
            "Amount": str(amount),
            "Authority": authority,
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                self._payment_verify_url,
                headers=headers,
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logger.error("ZarinPal payment_verify timeout, authority=%s", authority)
            return {"Status": 0, "error": "timeout"}
        except requests.exceptions.RequestException as e:
            logger.error("ZarinPal payment_verify failed: %s", e)
            return {"Status": 0, "error": "connection_error"}

        try:
            return response.json()
        except ValueError:
            logger.error("ZarinPal payment_verify returned non-JSON response")
            return {"Status": 0, "error": "invalid_response"}

    def generate_payment_url(self, authority):
        return self._payment_page_url + authority