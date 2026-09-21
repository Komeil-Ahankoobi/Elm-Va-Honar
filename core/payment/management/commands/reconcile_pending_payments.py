import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from order.models import InsufficientStockError, OrderModel
from payment.models import PaymentModel, PaymentStatusType
from payment.views import DEFINITIVE_FAILURE_CODES
from payment.zarinpal_client import ZarinPalClient

logger = logging.getLogger(__name__)

# پرداختی که کمتر از این مدت از ساختنش گذشته را دست نمی‌زنیم
# (شاید کاربر هنوز در صفحه‌ی درگاه باشد).
MIN_AGE_MINUTES = 5

# فقط بعد از این مدت، و فقط اگر زرین‌پال صریحاً بگوید پرداخت نشده،
# پرداخت را «ناموفق» ثبت می‌کنیم.
FAIL_AFTER_MINUTES = 60


class Command(BaseCommand):
    help = (
        "پرداخت‌های «در انتظار» که برگشتشان از درگاه به سایت نرسیده را "
        "از زرین‌پال استعلام می‌کند."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--min-age",
            type=int,
            default=MIN_AGE_MINUTES,
            help="حداقل سنِ پرداخت (دقیقه) برای بررسی",
        )
        parser.add_argument(
            "--fail-after",
            type=int,
            default=FAIL_AFTER_MINUTES,
            help="بعد از چند دقیقه، پرداختِ پرداخت‌نشده ناموفق ثبت شود",
        )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(minutes=options["min_age"])
        payment_ids = list(
            PaymentModel.objects.filter(
                status=PaymentStatusType.pending.value,
                created_date__lt=cutoff,
            ).values_list("pk", flat=True)
        )

        client = ZarinPalClient()
        counts = {"confirmed": 0, "refund": 0, "failed": 0, "waiting": 0, "skipped": 0}

        for payment_pk in payment_ids:
            outcome = self._reconcile(payment_pk, client, options["fail_after"])
            counts[outcome] += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"بررسی شد: {len(payment_ids)} | تأییدشده: {counts['confirmed']} | "
                f"نیازمند بازگشت پول: {counts['refund']} | ناموفق: {counts['failed']} | "
                f"در انتظار: {counts['waiting']} | ردشده: {counts['skipped']}"
            )
        )

    def _reconcile(self, payment_pk, client, fail_after_minutes):
        order_id = (
            PaymentModel.objects.filter(pk=payment_pk)
            .values_list("order_id", flat=True)
            .first()
        )
        if order_id is None:
            return "skipped"

        with transaction.atomic():
            # ترتیبِ قفل‌ها مثل صفحه‌ی تأیید پرداخت: اول سفارش، بعد پرداخت.
            order = OrderModel.objects.select_for_update().get(pk=order_id)
            payment = PaymentModel.objects.select_for_update().get(pk=payment_pk)

            # در این فاصله شاید برگشتِ کاربر نتیجه را ثبت کرده باشد.
            if payment.status != PaymentStatusType.pending.value:
                return "skipped"

            result = client.payment_verify(int(payment.amount), payment.authority_id)

            # پرداخت انجام شده بوده و تأیید شد
            if result["ok"]:
                payment.ref_id = result["ref_id"]
                payment.card_pan = result["card_pan"] or ""
                payment.card_hash = result["card_hash"] or ""
                payment.response_code = result["code"]
                payment.response_json = result["raw"]
                payment.status = PaymentStatusType.success.value
                payment.save()

                try:
                    order.confirm_payment()
                except InsufficientStockError:
                    order.cancel_payment()
                    logger.error(
                        "Paid but out of stock, refund needed: payment=%s order=%s",
                        payment.pk,
                        order.pk,
                    )
                    return "refund"
                return "confirmed"

            # زرین‌پال صریحاً می‌گوید پرداخت نشده
            if result["code"] in DEFINITIVE_FAILURE_CODES:
                age = timezone.now() - payment.created_date
                if age >= timedelta(minutes=fail_after_minutes):
                    payment.response_code = result["code"]
                    payment.response_json = result["raw"]
                    payment.status = PaymentStatusType.failed.value
                    payment.save()
                    return "failed"
                return "waiting"

            # خطای شبکه یا پاسخ نامشخص: دست نمی‌زنیم، دفعه‌ی بعد دوباره تلاش می‌شود.
            logger.warning(
                "Reconcile uncertain: payment=%s order=%s code=%s message=%s",
                payment.pk,
                order.pk,
                result["code"],
                result["message"],
            )
            return "skipped"