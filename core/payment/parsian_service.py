"""
منطق مشترکِ «نتیجه‌گیری» پرداخت پارسیان؛ هم ویوی callback و هم دستور reconcile
از همین تابع استفاده می‌کنند تا رفتارشان دقیقاً یکی باشد.
"""

import logging

from django.conf import settings
from django.db import transaction

from order.models import InsufficientStockError, OrderModel, OrderStatusType

from .models import PaymentModel, PaymentStatusType
from .parsian_client import ParsianClient

logger = logging.getLogger(__name__)


def rial_amount(toman):
    """مبلغ سایت (تومان) → مبلغ ارسالی به بانک (ریال)."""
    return int(toman) * int(getattr(settings, "PARSIAN_AMOUNT_MULTIPLIER", 10))


def settle_parsian_payment(
    payment_pk, *, client=None, callback_failed=False, callback_rrn=None
):
    """
    یک پرداخت «در انتظار» پارسیان را نتیجه‌گیری می‌کند.

    خروجی: (outcome, order_id)
      confirmed        پرداخت تأیید شد و سفارش پرداخت‌شده ثبت شد
      already_success  قبلاً موفق ثبت شده بود
      failed           ناموفق (انصراف کاربر یا قبلاً ناموفق ثبت شده)
      expired_reversed سفارش دیگر در حال پرداخت نبود؛ پرداخت برگشت داده شد
      stock_reversed   پول گرفته شد ولی موجودی تمام شده بود؛ برگشت داده شد
      stock_refund     مثل بالا ولی برگشت خودکار انجام نشد → بازگشت دستی لازم است
      uncertain        نتیجه مشخص نیست؛ پرداخت «در انتظار» می‌ماند
      missing          پرداخت پیدا نشد
    """
    order_id = (
        PaymentModel.objects.filter(pk=payment_pk)
        .values_list("order_id", flat=True)
        .first()
    )
    if order_id is None:
        return "missing", None

    client = client or ParsianClient()

    # ترتیب قفل‌ها مثل زرین‌پال: اول سفارش، بعد پرداخت.
    with transaction.atomic():
        order = OrderModel.objects.select_for_update().get(pk=order_id)
        payment = PaymentModel.objects.select_for_update().get(pk=payment_pk)

        # نتیجه‌ی این پرداخت قبلاً مشخص شده؛ دوباره تأیید نمی‌کنیم (idempotent).
        if payment.status != PaymentStatusType.pending.value:
            if payment.status == PaymentStatusType.success.value:
                return "already_success", order.pk
            return "failed", order.pk

        # بانک در callback گفته پرداخت انجام نشده (مثلاً انصراف کاربر).
        if callback_failed:
            payment.status = PaymentStatusType.failed.value
            payment.save(update_fields=["status", "updated_date"])
            if order.status == OrderStatusType.pending.value:
                order.cancel_payment()
            return "failed", order.pk

        token = int(payment.authority_id)

        # سفارش دیگر «در حال پرداخت» نیست (منقضی/لغو شده): تأیید نمی‌کنیم،
        # پرداخت را برمی‌گردانیم تا پول به کاربر برگردد.
        if order.status != OrderStatusType.pending.value:
            reversal = client.payment_reversal(token)
            payment.response_json = {"reversal": reversal["raw"]}
            if reversal["ok"]:
                payment.response_code = reversal["code"]
                payment.status = PaymentStatusType.failed.value
                payment.save()
                logger.warning(
                    "Parsian payment reversed (order not pending): payment=%s order=%s",
                    payment.pk,
                    order.pk,
                )
                return "expired_reversed", order.pk
            payment.save(update_fields=["response_json", "updated_date"])
            logger.warning(
                "Parsian reversal not confirmed (order not pending): "
                "payment=%s order=%s code=%s",
                payment.pk,
                order.pk,
                reversal["code"],
            )
            return "uncertain", order.pk

        # --- تأیید پرداخت ---
        result = client.payment_verify(token)

        if not result["ok"]:
            # شبکه قطع، timeout، یا بانک «تأیید نشد» گفته. نمی‌دانیم پول رفته یا نه،
            # پس ناموفق ثبت نمی‌کنیم. اگر پول رفته باشد و تأیید نشود بانک خودش برمی‌گرداند.
            logger.warning(
                "Parsian confirm not ok: payment=%s order=%s code=%s",
                payment.pk,
                order.pk,
                result["code"],
            )
            return "uncertain", order.pk

        payment.ref_id = result["ref_id"] or callback_rrn
        payment.card_pan = result["card_pan"] or ""
        payment.card_hash = result["card_hash"] or ""
        payment.response_code = result["code"]
        payment.response_json = result["raw"]
        payment.status = PaymentStatusType.success.value
        payment.save()

        try:
            order.confirm_payment()
        except InsufficientStockError:
            # پول دریافت و تأیید شد ولی موجودی همین حالا تمام شده.
            order.cancel_payment()
            reversal = client.payment_reversal(token)
            payment.response_json = {
                "confirm": result["raw"],
                "reversal": reversal["raw"],
            }
            if reversal["ok"]:
                payment.status = PaymentStatusType.failed.value
                payment.response_code = reversal["code"]
            payment.save()
            logger.error(
                "Paid but out of stock: payment=%s order=%s reversal_ok=%s",
                payment.pk,
                order.pk,
                reversal["ok"],
            )
            return ("stock_reversed" if reversal["ok"] else "stock_refund"), order.pk

        return "confirmed", order.pk