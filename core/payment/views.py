from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from cart.cart import CartSession
from order.models import InsufficientStockError, OrderModel, OrderStatusType
from .models import PaymentModel, PaymentStatusType
from .zarinpal_client import ZarinPalClient
import logging


logger = logging.getLogger(__name__)
DEFINITIVE_FAILURE_CODES = {-50, -51, -53, -54, -55}


class PaymentRequestView(LoginRequiredMixin, View):
    def get(self, request, order_id, *args, **kwargs):
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

            amount = int(order.total_price)

            existing_pending = (
                PaymentModel.objects.select_for_update()
                .filter(order=order, status=PaymentStatusType.pending.value)
                .first()
            )

            # برای همین سفارش پرداخت در جریان داریم؛ همان را ادامه می‌دهیم.
            # اینطوری دبل‌کلیک یا رفرش، Authority جدید نمی‌سازد و
            # Authority قبلی (که شاید کاربر با آن پرداخت کند) بی‌اعتبار نمی‌شود.
            if existing_pending and existing_pending.amount == amount:
                return redirect(
                    client.generate_payment_url(existing_pending.authority_id)
                )

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