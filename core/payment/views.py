import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from cart.cart import CartSession
from order.models import InsufficientStockError, OrderModel, OrderStatusType

from .gateways import GatewayType, available_gateways
from .models import PaymentModel, PaymentStatusType
from .parsian_client import ParsianClient
from .parsian_service import rial_amount, settle_parsian_payment
from .zarinpal_client import ZarinPalClient

logger = logging.getLogger(__name__)

DEFINITIVE_FAILURE_CODES = {-50, -51, -53, -54, -55}


class PaymentRequestView(LoginRequiredMixin, View):
    def get(self, request, order_id, *args, **kwargs):
        # درگاه باید صریحاً انتخاب شده باشد و برای این کاربر مجاز باشد.
        gateway = request.GET.get("gateway", "")
        allowed = [code for code, _label in available_gateways(request.user)]
        if gateway not in allowed:
            messages.error(request, "لطفاً یکی از درگاه‌های پرداخت را انتخاب کنید.")
            return redirect(reverse_lazy("order:order-failed"))

        is_parsian = gateway == GatewayType.parsian.value
        if is_parsian:
            client = ParsianClient(
                callback_url=request.build_absolute_uri(reverse("payment:verify-parsian"))
            )
        else:
            client = ZarinPalClient(
                callback_url=request.build_absolute_uri(reverse("payment:verify"))
            )

        with transaction.atomic():
            # قفل روی خودِ سفارش: اگه دو درخواست هم‌زمان برای یک سفارش بیاد
            # (دبل‌کلیک یا چند تب)، دومی صبر می‌کنه تا اولی تموم بشه.
            order = get_object_or_404(
                OrderModel.objects.select_for_update(),
                pk=order_id,
                user=request.user,
            )

            # سفارش قبلاً پرداخت شده؛ دوباره پرداخت نمی‌سازیم.
            if order.is_successful:
                return redirect(
                    reverse("order:order-success", kwargs={"order_id": order.pk})
                )

            # فقط سفارشِ «در حال پرداخت» که هنوز منقضی نشده اجازه پرداخت دارد.
            if (
                order.status != OrderStatusType.pending.value
                or order.is_pending_expired
            ):
                messages.error(
                    request,
                    "این سفارش دیگر قابل پرداخت نیست. لطفاً دوباره سفارش ثبت کنید.",
                )
                return redirect(reverse_lazy("order:order-failed"))

            amount = int(order.total_price)  # تومان

            existing_pending = (
                PaymentModel.objects.select_for_update()
                .filter(order=order, status=PaymentStatusType.pending.value)
                .first()
            )

            # پرداخت در جریان با «درگاه دیگری» داریم؛ نباید همزمان دو درگاه باز شود.
            if existing_pending and existing_pending.gateway != gateway:
                messages.error(
                    request,
                    "برای این سفارش پرداخت با درگاه دیگری در جریان است. "
                    "چند دقیقه صبر کنید و دوباره تلاش کنید.",
                )
                return redirect(reverse_lazy("order:order-failed"))

            # برای همین سفارش پرداخت در جریانِ همین درگاه داریم؛ همان را ادامه می‌دهیم.
            # اینطوری دبل‌کلیک یا رفرش، Authority/Token جدید نمی‌سازد و
            # قبلی (که شاید کاربر با آن پرداخت کند) بی‌اعتبار نمی‌شود.
            if existing_pending and existing_pending.amount == amount:
                return redirect(
                    client.generate_payment_url(existing_pending.authority_id)
                )

            if is_parsian:
                # OrderId ارسالی به بانک برای هر تلاش یکتاست: شماره‌ی سفارش × ۱۰۰ + شماره‌ی تلاش
                attempt = min(PaymentModel.objects.filter(order=order).count() + 1, 99)
                result = client.payment_request(
                    rial_amount(amount),
                    order_id=order.pk * 100 + attempt,
                    additional_data=f"order:{order.pk}",
                )
            else:
                result = client.payment_request(
                    amount,
                    description=f"پرداخت سفارش شماره {order.pk}",
                    email=getattr(request.user, "email", None) or None,
                    mobile=getattr(request.user, "phone_number", None) or None,
                    order_id=order.pk,
                )

            authority = result["authority"]
            if not result["ok"] or not authority:
                messages.error(
                    request, "اتصال به درگاه پرداخت برقرار نشد، دوباره تلاش کن"
                )
                # سفارش همان «در حال پرداخت» می‌ماند و وضعیتش را دست نمی‌زنیم.
                return redirect(reverse_lazy("order:order-failed"))

            if existing_pending:
                existing_pending.authority_id = authority
                existing_pending.amount = amount
                existing_pending.response_code = result["code"]
                existing_pending.response_json = result["raw"]
                existing_pending.save()
            else:
                PaymentModel.objects.create(
                    order=order,
                    gateway=gateway,
                    authority_id=authority,
                    amount=amount,
                    response_code=result["code"],
                    response_json=result["raw"],
                )

        return redirect(client.generate_payment_url(authority))


class PaymentVerifyView(View):
    def get(self, request, *args, **kwargs):
        authority_id = request.GET.get("Authority")
        gateway_status = request.GET.get("Status")

        if not authority_id:
            return redirect(reverse_lazy("order:order-failed"))

        order_id = get_object_or_404(PaymentModel, authority_id=authority_id).order_id

        with transaction.atomic():
            order = get_object_or_404(
                OrderModel.objects.select_for_update(), pk=order_id
            )
            payment_obj = get_object_or_404(
                PaymentModel.objects.select_for_update(),
                authority_id=authority_id,
            )

            # نتیجه‌ی این پرداخت قبلاً مشخص شده؛ دوباره تأیید نمی‌کنیم.
            if payment_obj.status != PaymentStatusType.pending.value:
                is_success = payment_obj.status == PaymentStatusType.success.value
                return redirect(
                    reverse_lazy("order:order-success", kwargs={"order_id": order.pk})
                    if is_success
                    else reverse_lazy("order:order-failed")
                )

            # کاربر در درگاه انصراف داده یا پرداخت ناموفق بوده.
            if gateway_status == "NOK":
                payment_obj.status = PaymentStatusType.failed.value
                payment_obj.save(update_fields=["status", "updated_date"])

                # فقط سفارشِ «در حال پرداخت» لغو می‌شود، نه سفارشِ پرداخت‌شده.
                if order.status == OrderStatusType.pending.value:
                    order.cancel_payment()

                return redirect(reverse_lazy("order:order-failed"))

            # Status نه OK است نه NOK (درخواست ناقص یا دستکاری‌شده):
            # هیچ چیزی را تغییر نمی‌دهیم.
            if gateway_status != "OK":
                return redirect(reverse_lazy("order:order-failed"))

            client = ZarinPalClient()
            result = client.payment_verify(
                int(payment_obj.amount), payment_obj.authority_id
            )

            # ۱) پرداخت تأیید شد
                        # ۱) پرداخت تأیید شد
            if result["ok"]:
                payment_obj.ref_id = result["ref_id"]
                payment_obj.card_pan = result["card_pan"] or ""
                payment_obj.card_hash = result["card_hash"] or ""
                payment_obj.response_code = result["code"]
                payment_obj.response_json = result["raw"]
                payment_obj.status = PaymentStatusType.success.value
                payment_obj.save()

                try:
                    order.confirm_payment()
                except InsufficientStockError:
                    # پول دریافت و تأیید شده، ولی موجودی کالا همین حالا تمام شده.
                    # سفارش لغو می‌شود و باید مبلغ به کاربر برگردانده شود
                    # (در ادمین: پرداختِ «موفق» با سفارشِ «لغو شده»).
                    order.cancel_payment()
                    logger.error(
                        "Paid but out of stock, refund needed: payment=%s order=%s",
                        payment_obj.pk,
                        order.pk,
                    )
                    messages.error(
                        request,
                        "پرداخت شما دریافت شد، اما موجودی یکی از کالاهای سفارش همین "
                        "حالا تمام شد و سفارش ثبت نشد. لطفاً با پشتیبانی تماس بگیرید "
                        f"و شماره‌ی سفارش {order.pk} را اعلام کنید تا مبلغ به حساب "
                        "شما برگردد.",
                    )
                    return redirect(reverse_lazy("order:order-failed"))

                # سبدِ سشن فقط اینجا قابل پاک‌کردن است چون به request نیاز دارد.
                CartSession(request.session).clear()

                return redirect(
                    reverse_lazy("order:order-success", kwargs={"order_id": order.pk})
                )

            # ۲) درگاه صریحاً گفته پرداخت انجام نشده
            if result["code"] in DEFINITIVE_FAILURE_CODES:
                payment_obj.response_code = result["code"]
                payment_obj.response_json = result["raw"]
                payment_obj.status = PaymentStatusType.failed.value
                payment_obj.save()

                logger.warning(
                    "Payment verify failed: payment=%s order=%s code=%s",
                    payment_obj.pk,
                    order.pk,
                    result["code"],
                )
                return redirect(reverse_lazy("order:order-failed"))

            # ۳) وضعیت نامشخص (قطعی اینترنت، timeout، خطای خود درگاه):
            # ممکن است کاربر واقعاً پول داده باشد. پرداخت را «ناموفق» نمی‌کنیم
            # و در همان حالت «در انتظار» می‌ماند تا بعداً دوباره تأیید شود.
            logger.error(
                "Payment verify uncertain: payment=%s order=%s code=%s message=%s",
                payment_obj.pk,
                order.pk,
                result["code"],
                result["message"],
            )
            messages.warning(
                request,
                "وضعیت پرداخت شما هنوز مشخص نشده است. اگر مبلغ از حساب شما کم شده، "
                "لطفاً کمی بعد وضعیت سفارش را در «سفارش‌های من» بررسی کنید "
                "یا با پشتیبانی تماس بگیرید.",
            )
            return redirect(reverse_lazy("order:order-failed"))


# پیام کاربر برای هر نتیجه‌ی پارسیان: (سطح پیام، متن)
_PARSIAN_MESSAGES = {
    "expired_reversed": (
        "error",
        "مهلت پرداخت این سفارش تمام شده بود، بنابراین سفارش ثبت نشد. "
        "اگر مبلغی از حساب شما کسر شده، حداکثر تا ۷۲ ساعت به حساب شما برمی‌گردد.",
    ),
    "stock_reversed": (
        "error",
        "موجودی یکی از کالاهای سفارش همین حالا تمام شد و سفارش ثبت نشد. "
        "مبلغ پرداختی شما به حساب شما برگردانده می‌شود.",
    ),
    "stock_refund": (
        "error",
        "پرداخت شما دریافت شد، اما موجودی یکی از کالاهای سفارش همین حالا تمام شد "
        "و سفارش ثبت نشد. لطفاً با پشتیبانی تماس بگیرید و شماره‌ی سفارش "
        "{order_id} را اعلام کنید تا مبلغ به حساب شما برگردد.",
    ),
    "uncertain": (
        "warning",
        "وضعیت پرداخت شما هنوز مشخص نشده است. اگر مبلغ از حساب شما کم شده، "
        "لطفاً کمی بعد وضعیت سفارش را در «سفارش‌های من» بررسی کنید "
        "یا با پشتیبانی تماس بگیرید.",
    ),
}


@method_decorator(csrf_exempt, name="dispatch")
class ParsianVerifyView(View):
    """
    callback پارسیان. بانک کاربر را (احتمالاً با POST) به این آدرس برمی‌گرداند.

    نکات مهم:
    - csrf_exempt لازم است، چون درخواست از سایت بانک می‌آید.
    - ورودی‌های callback از مرورگر کاربر می‌آیند و قابل جعل‌اند؛ هرگز بر اساس آن‌ها
      پرداخت را «موفق» نمی‌کنیم. موفقیت فقط با Confirm سمت سرور ثبت می‌شود.
    - به request.session دست نمی‌زنیم: کوکی سشن در POST بین‌سایتی نمی‌آید و ساختن
      سشن جدید، سشن واقعی کاربر را overwrite و او را logout می‌کرد.
    """

    http_method_names = ["get", "post"]

    def get(self, request, *args, **kwargs):
        params = {k.lower(): v for k, v in request.GET.items()}
        params.update({k.lower(): v for k, v in request.POST.items()})
        logger.info("Parsian callback params: %s", params)

        token = (params.get("token") or "").strip()
        if not token.isdigit():
            messages.error(request, "اطلاعات بازگشت از درگاه نامعتبر است.")
            return redirect(reverse_lazy("order:order-failed"))

        payment = PaymentModel.objects.filter(
            gateway=GatewayType.parsian.value, authority_id=token
        ).first()
        if payment is None:
            logger.warning("Parsian callback with unknown token: %s", token)
            messages.error(request, "تراکنش پیدا نشد.")
            return redirect(reverse_lazy("order:order-failed"))

        # مطابق نمونه‌کد رسمی پارسیان: فقط اگر status == 0 و RRN > 0 باشد سراغ Confirm
        # می‌رویم؛ در غیر این صورت (انصراف کاربر، خطا، نبودن RRN) پرداخت انجام نشده است.
        try:
            cb_status = int(str(params.get("status", "")).strip())
        except ValueError:
            cb_status = None
        try:
            cb_rrn = int(str(params.get("rrn", "")).strip())
        except ValueError:
            cb_rrn = None
        callback_ok = cb_status == 0 and bool(cb_rrn and cb_rrn > 0)

        outcome, order_id = settle_parsian_payment(
            payment.pk,
            callback_failed=not callback_ok,
            callback_rrn=cb_rrn if callback_ok else None,
        )

        if outcome in ("confirmed", "already_success"):
            return redirect(
                reverse_lazy("order:order-success", kwargs={"order_id": order_id})
            )

        level, text = _PARSIAN_MESSAGES.get(outcome, (None, None))
        if text:
            getattr(messages, level)(request, text.format(order_id=order_id))
        return redirect(reverse_lazy("order:order-failed"))

    post = get