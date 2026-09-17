from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View

from cart.cart import CartSession
from order.models import OrderModel
from .models import PaymentModel, PaymentStatusType
from .zarinpal_client import ZarinPalClient


class PaymentRequestView(View):
    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(OrderModel, pk=order_id, user=request.user)

        amount = int(order.total_price)

        with transaction.atomic():
            existing_pending = (
                PaymentModel.objects.select_for_update()
                .filter(order=order, status=PaymentStatusType.pending)
                .first()
            )

            client = ZarinPalClient(
                callback_url=request.build_absolute_uri(reverse("payment:verify"))
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
                # نکته: cancel_payment اگه هنوز هیچ PaymentModel ای برای این
                # order ساخته نشده باشه، کل order رو حذف می‌کنه (طبق
                # order/models.py). به همین خاطر order-failed هم در
                # urls.py هیچ آرگومانی نمی‌گیره؛ بعد از این خط دیگه
                # نمی‌شه به order.pk رفرنس داد.
                order.cancel_payment()
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

        with transaction.atomic():
            payment_obj = get_object_or_404(
                PaymentModel.objects.select_for_update(),
                authority_id=authority_id,
            )
            order = payment_obj.order

            # اگر قبلاً نتیجه‌اش مشخص شده، دوباره verify نمی‌کنیم.
            # اینجا حتماً PaymentModel وجود داره پس order هرگز به‌خاطر
            # cancel_payment حذف نشده و order.pk معتبره.
            if payment_obj.status != PaymentStatusType.pending.value:
                is_success = payment_obj.status == PaymentStatusType.success.value
                return redirect(
                    reverse_lazy("order:order-success", kwargs={"order_id": order.pk})
                    if is_success
                    else reverse_lazy("order:order-failed")
                )

            # طبق مستندات، فقط وقتی Status برابر OK است باید verify صدا زده شود.
            if gateway_status != "OK":
                payment_obj.status = PaymentStatusType.failed.value
                payment_obj.save(update_fields=["status", "updated_date"])
                order.cancel_payment()
                return redirect(reverse_lazy("order:order-failed"))

            client = ZarinPalClient()
            result = client.payment_verify(
                int(payment_obj.amount), payment_obj.authority_id
            )

            is_success = result["ok"]

            payment_obj.ref_id = result["ref_id"]
            payment_obj.card_pan = result["card_pan"] or ""
            payment_obj.card_hash = result["card_hash"] or ""
            payment_obj.response_code = result["code"]
            payment_obj.response_json = result["raw"]
            payment_obj.status = (
                PaymentStatusType.success.value
                if is_success
                else PaymentStatusType.failed.value
            )
            payment_obj.save()

            if is_success:
                # وضعیت سفارش، مصرف‌شدنِ کد تخفیف، کم‌کردنِ موجودی، و خالی‌کردنِ
                # سبد خریدِ دیتابیسی همگی داخل confirm_payment و اتمیک انجام می‌شن.
                order.confirm_payment()
                # سبدِ سشن (برای کاربر مهمان/مرورگر) فقط اینجا قابل پاک‌کردنه
                # چون به request نیاز داره.
                CartSession(request.session).clear()
            else:
                order.cancel_payment()

        return redirect(
            reverse_lazy("order:order-success", kwargs={"order_id": order.pk})
            if is_success
            else reverse_lazy("order:order-failed")
        )