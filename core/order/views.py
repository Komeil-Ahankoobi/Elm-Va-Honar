from django.views.generic import FormView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from decimal import Decimal
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db import IntegrityError

from dashboard.permissions import HasCustomerAccessPermission
from cart.utils import get_cart
from order.models import (
    UserAddressModel,
    OrderModel,
    OrderItemsModel,
    CoponModel,
    PostPrice,
    InsufficientStockError
)
from .forms import OrderCheckoutForm
from cart.models import CartModel
from shop.models import ProductStatusType


class OrderCheckoutView(LoginRequiredMixin, HasCustomerAccessPermission, FormView):
    template_name = "order/order-checkout.html"
    form_class = OrderCheckoutForm  

    def form_valid(self, form):
        user = self.request.user

        # اول سفارش‌های pending قدیمیِ منقضی‌شده‌ی همین کاربر رو پاک‌سازی
        # می‌کنیم (شاید همین الان زمانش تموم شده و بشه ادامه داد).
        OrderModel.expire_stale_pending()

        # اگه هنوز یه سفارش pending فعال (منقضی‌نشده) داره، اجازه نمی‌دیم
        # سفارش جدید بسازه؛ باید صبر کنه تا همون تموم بشه یا زمانش سر بیاد.
        # عمداً اینجا دیگه ریدایرکتش نمی‌کنیم به همون سفارشِ قبلی، چون
        # ممکنه کاربر توی همین فاصله سبدش رو عوض کرده باشه (تعداد/محصول
        # جدید اضافه کرده باشه) و سفارش قدیمی دیگه با سبد فعلی‌ش هم‌خوانی
        # نداشته باشه.
        active_pending_order = OrderModel.get_active_pending_order(user)
        if active_pending_order:
            response = self.redirect_if_double_submit(active_pending_order)
            if response:
                return response
            remaining_minutes = (active_pending_order.seconds_remaining // 60) + 1
            messages.warning(
                self.request,
                f"شما یک پرداخت در حال انجام دارید. لطفاً  {remaining_minutes} "
                "دقیقه دیگر صبر کنید ، سپس دوباره تلاش کنید.",
            )
            return self.render_to_response(self.get_context_data(form=form))

        cleaned_data = form.cleaned_data
        address = cleaned_data["address_id"]
        copon = cleaned_data["copon"]

        cart = CartModel.objects.filter(user=user).first()
        if cart is None or not cart.cart_items.exists():
            messages.error(self.request, "سبد خرید شما خالی است.")
            return redirect(reverse_lazy("order:order-failed"))

        invalid_items = self.find_invalid_items(cart)
        if invalid_items:
            item_names = "، ".join(item.product.title for item in invalid_items)
            messages.error(
                self.request,
                f"این محصولات دیگر قابل خرید نیستند، لطفاً از سبد خرید حذفشان کنید: {item_names}",
            )
            return redirect(reverse_lazy("order:order-failed"))

        insufficient_items = self.check_stock_availability(cart)
        if insufficient_items:
            item_names = "، ".join(item.product.title for item in insufficient_items)
            messages.error(
                self.request, f"موجودی کافی برای این محصولات نیست: {item_names}"
            )
            return redirect(reverse_lazy("order:order-failed"))

        try:
            with transaction.atomic():
                try:
                    # یک نقطه‌ی برگشتِ جداگانه: اگر سفارشِ در حال پرداختِ دیگری همین الان
                    # ساخته شده باشد، فقط همین بخش برگردانده می‌شود و تراکنشِ اصلی سالم می‌ماند.
                    with transaction.atomic():
                        order = self.create_order(address)
                except IntegrityError:
                    response = self.redirect_if_double_submit(
                        OrderModel.get_active_pending_order(user)
                    )
                    if response:
                        return response
                    # race condition: یه request موازی همین الان سفارش pending
                    # ساخته (مثلاً دو تب هم‌زمان). به‌جای ساخت سفارش دوم، همون
                    # پیام «صبر کن» رو نشون می‌دیم، نه ریدایرکت به پرداخت.
                    messages.warning(
                        self.request,
                        "شما یک پرداخت در حال انجام دارید. لطفاً کمی صبر کنید و دوباره تلاش کنید.",
                    )
                    return self.render_to_response(self.get_context_data(form=form))

                self.create_order_items(cart, order)
                subtotal_price = order.calculate_total_price()
                self.apply_copon_pricing(copon, subtotal_price, order)
                order.save()

                # موجودی همین‌جا برای این سفارش رزرو (از انبار کم) می‌شود.
                # اگر کالایی همین الان تمام شده باشد، کل این بلوک (سفارش و آیتم‌ها)
                # برگردانده می‌شود و کاربر اصلاً به درگاه نمی‌رود.
                order.reserve_stock()
        except InsufficientStockError as error:
            messages.error(
                self.request, f"موجودی کافی برای این محصول نیست: {error}"
            )
            return redirect(reverse_lazy("order:order-failed"))

        return redirect(reverse("payment:request", kwargs={"order_id": order.id}))


    def redirect_if_double_submit(self, order):
        """
        اگر سفارشِ در حال پرداخت همین چند ثانیه‌ی پیش ساخته شده، یعنی کاربر
        دو بار دکمه را زده؛ به‌جای پیام «صبر کنید» به همان سفارش ادامه می‌دهیم.
        """
        if order is None:
            return None
        age = (timezone.now() - order.created_date).total_seconds()
        if age < 10:
            return redirect(reverse("payment:request", kwargs={"order_id": order.id}))
        return None
    

    def form_invalid(self, form):
        for errors in form.errors.values():
            for error in errors:
                messages.error(self.request, error)
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


    def find_invalid_items(self, cart):
        """آیتم‌هایی از سبد که با محصول یا وریانتِ واقعی هم‌خوانی ندارند."""
        invalid_items = []
        for item in cart.cart_items.select_related("product", "variant"):
            product = item.product
            variant = item.variant
            if product.status != ProductStatusType.publish.value:
                invalid_items.append(item)
            elif variant is not None and (
                variant.product_id != product.pk
                or variant.status != ProductStatusType.publish.value
            ):
                invalid_items.append(item)
            elif variant is None and product.has_variants():
                invalid_items.append(item)
        return invalid_items


    def apply_copon_pricing(self, copon, subtotal_price, order):
        order.subtotal_price = subtotal_price
        post_price = PostPrice.load().price

        if copon:
            discount_price = round(
                subtotal_price * (Decimal(copon.discount_percent) / Decimal("100"))
            )
            order.copon = copon
            order.copon_code = copon.code
            order.copon_discount_percent = copon.discount_percent
            order.discount_amount = discount_price
            order.total_price = subtotal_price - discount_price + post_price
        else:
            order.discount_amount = 0
            order.total_price = subtotal_price + post_price

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
        post_price = PostPrice.load().price
        context["price"] = price
        context["post_price"] = post_price
        context["total_price"] = price + post_price

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class OrderSuccessView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = "order/success.html"

    def get(self, request, *args, **kwargs):
        order = get_object_or_404(
            OrderModel, pk=kwargs["order_id"], user=request.user
        )

        if not order.is_successful:
            return redirect(reverse_lazy("order:order-failed"))

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        post_price = PostPrice.load().price
        total_price = cart.calculate_total_price()
        discount_percent = Decimal(copon.discount_percent) / Decimal("100")
        total_price = round(total_price - (total_price * discount_percent), 0)
        total_price = total_price + post_price

        return JsonResponse(
            {
                "message": "کد تخفیف با موفقیت ثبت شد",
                "post_price": post_price,
                "total_price": total_price,
            },
            status=200,
        )