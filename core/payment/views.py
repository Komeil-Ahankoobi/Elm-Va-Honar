from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View

from order.models import OrderModel, OrderStatusType
from .models import PaymentModel, PaymentStatusType
from .zarinpal_client import ZarinPalSandbox


class PaymentRequestView(View):
    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(OrderModel, pk=order_id, user=request.user)

        amount = order.total_price

        with transaction.atomic():
            existing_pending = (
                PaymentModel.objects.select_for_update()
                .filter(order=order, status=PaymentStatusType.pending)
                .first()
            )

            zarin_pal = ZarinPalSandbox(
                callback_url=request.build_absolute_uri(reverse("payment:verify"))
            )
            response = zarin_pal.payment_request(int(amount))

            status_code = response.get("Status")
            authority = response.get("Authority")

            if status_code != 100 or not authority:
                messages.error(request, "اتصال به درگاه پرداخت برقرار نشد، دوباره تلاش کن")
                return redirect(reverse_lazy("order:order-failed"))

            if existing_pending:
                existing_pending.authority_id = authority
                existing_pending.amount = amount
                existing_pending.response_json = response
                existing_pending.save()
            else:
                PaymentModel.objects.create(
                    order=order,
                    authority_id=authority,
                    amount=amount,
                    response_json=response,
                )

        return redirect(zarin_pal.generate_payment_url(authority))


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

            if payment_obj.status != PaymentStatusType.pending.value:
                is_success = payment_obj.status == PaymentStatusType.success.value
                return redirect(
                    reverse_lazy("order:order-success") if is_success
                    else reverse_lazy("order:order-failed")
                )

            if gateway_status != "OK":
                payment_obj.status = PaymentStatusType.failed.value
                payment_obj.save(update_fields=["status", "updated_date"])
                order.status = OrderStatusType.faild.value
                order.save(update_fields=["status", "updated_date"])
                return redirect(reverse_lazy("order:order-failed"))

            zarin_pal = ZarinPalSandbox()
            response = zarin_pal.payment_verify(
                int(payment_obj.amount), payment_obj.authority_id
            )

            status_code = response.get("Status")
            ref_id = response.get("RefID")
            is_success = status_code in {100, 101}

            payment_obj.ref_id = ref_id
            payment_obj.response_code = status_code
            payment_obj.response_json = response
            payment_obj.status = (
                PaymentStatusType.success.value if is_success
                else PaymentStatusType.failed.value
            )
            payment_obj.save()

            if is_success:
                self.decrease_stock(order)
                order.status = OrderStatusType.succes.value
            else:
                order.status = OrderStatusType.faild.value
            order.save()

        return redirect(
            reverse_lazy("order:order-success") if is_success
            else reverse_lazy("order:order-failed")
        )

    def decrease_stock(self, order):
        for item in order.items.select_related("product", "variant"):
            stock_obj = item.variant if item.variant else item.product
            model_class = type(stock_obj)

            locked_obj = model_class.objects.select_for_update().get(pk=stock_obj.pk)
            current_stock = locked_obj.stock or 0
            locked_obj.stock = max(current_stock - item.quantity, 0)
            locked_obj.save(update_fields=["stock"])
            locked_obj.sync_visibility_from_stock()