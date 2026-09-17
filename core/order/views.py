from django.views.generic import FormView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from decimal import Decimal
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils import timezone

from dashboard.permissions import HasCustomerAccessPermission
from cart.utils import get_cart
from order.models import (
    UserAddressModel,
    OrderModel,
    OrderItemsModel,
    CoponModel,
)
from .forms import OrderCheckoutForm
from cart.models import CartModel


class OrderCheckoutView(LoginRequiredMixin, HasCustomerAccessPermission, FormView):
    template_name = "order/order-checkout.html"
    form_class = OrderCheckoutForm

    def form_valid(self, form):
        user = self.request.user
        cleaned_data = form.cleaned_data
        address = cleaned_data["address_id"]
        copon = cleaned_data["copon"]

        cart = CartModel.objects.get(user=user)

        insufficient_items = self.check_stock_availability(cart)
        if insufficient_items:
            item_names = "، ".join(item.product.title for item in insufficient_items)
            messages.error(
                self.request, f"موجودی کافی برای این محصولات نیست: {item_names}"
            )
            return redirect(reverse_lazy("order:order-failed"))

        with transaction.atomic():
            order = self.create_order(address)
            self.create_order_items(cart, order)

            subtotal_price = order.calculate_total_price()
            self.apply_copon_pricing(copon, subtotal_price, order)
            order.save()

        # return redirect(reverse("payment:request", kwargs={"order_id": order.id}))
        return redirect(reverse("order:order-success", kwargs={"order_id": order.id}))

    def form_invalid(self, form):
        return redirect(reverse_lazy("order:order-failed"))

    def check_stock_availability(self, cart):

        insufficient_items = []
        for item in cart.cart_items.all():
            stock_source = item.variant if item.variant else item.product
            available_stock = getattr(stock_source, "stock", None)
            if available_stock is None:
                continue
            if item.quantity > available_stock:
                insufficient_items.append(item)
        return insufficient_items

    def apply_copon_pricing(self, copon, subtotal_price, order):
        order.subtotal_price = subtotal_price

        if copon:
            discount_price = round(
                subtotal_price * (Decimal(copon.discount_percent) / Decimal("100"))
            )
            order.copon = copon
            order.copon_code = copon.code
            order.copon_discount_percent = copon.discount_percent
            order.discount_amount = discount_price
            order.total_price = subtotal_price - discount_price
        else:
            order.discount_amount = 0
            order.total_price = subtotal_price

    def create_order(self, address):
        return OrderModel.objects.create(
            user=self.request.user,
            address=address.address,
            state=address.state,
            city=address.city,
            zip_code=address.zip_code,
        )

    def create_order_items(self, cart, order):
        for item in cart.cart_items.all():
            price_source = item.variant if item.variant else item.product
            OrderItemsModel.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                original_price=price_source.price,
                discount_percent=price_source.discount_percent or 0,
                price=price_source.get_price(),
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["addresses"] = UserAddressModel.objects.filter(user=self.request.user)

        cart = get_cart(self.request)
        price = cart.get_total_payment_amount()
        total_tax = round(price * 10 / 100)
        context["price"] = price
        context["total_tax"] = total_tax
        context["total_price"] = price + total_tax

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class OrderSuccessView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = "order/success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        context["cart_items"] = cart.get_cart_items()
        context["order_id"] = self.kwargs["order_id"]
        return context


class OrderFailedView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = "order/failed.html"


class ValidateCoponView(LoginRequiredMixin, HasCustomerAccessPermission, View):

    def post(self, *args, **kwargs):
        code = self.request.POST.get("code")
        user = self.request.user

        if not code:
            return JsonResponse({"message": "کد تخفیف وارد نشده است"}, status=400)

        try:
            copon = CoponModel.objects.get(code=code)
        except CoponModel.DoesNotExist:
            return JsonResponse({"message": "کد تخفیف یافت نشد"}, status=404)

        if copon.is_usage_limit_reached:
            return JsonResponse(
                {"message": "حد استفاده از کد تخفیف به اتمام رسیده است"}, status=403
            )

        if copon.expiration_date and copon.expiration_date < timezone.now():
            return JsonResponse({"message": "کد تخفیف منقضی شده است"}, status=403)

        if copon.is_used_by(user):
            return JsonResponse(
                {"message": "این کد تخفیف قبلا توسط شما استفاده شده است"}, status=403
            )

        try:
            cart = CartModel.objects.get(user=user)
        except CartModel.DoesNotExist:
            return JsonResponse({"message": "سبد خرید یافت نشد"}, status=404)

        total_price = cart.calculate_total_price()
        discount_percent = Decimal(copon.discount_percent) / Decimal("100")
        total_price = round(total_price - (total_price * discount_percent), 0)
        total_tax = round((total_price * Decimal("10")) / Decimal("100"), 0)

        return JsonResponse(
            {
                "message": "کد تخفیف با موفقیت ثبت شد",
                "total_tax": total_tax,
                "total_price": total_price,
            },
            status=200,
        )
