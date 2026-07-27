from django.views.generic import (
    FormView,
    TemplateView,
    View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils import timezone

from dashboard.permissions import HasCustomerAccessPermission
from cart.utils import get_cart
from order.models import (
    UserAddressModel,
    OrderModel,
    OrderItemsModel,
    CoponModel 
)
from .forms import OrderCheckoutForm
from cart.models import CartModel
from cart.cart import CartSession

# Create your views here.
class OrderCheckoutView(LoginRequiredMixin, HasCustomerAccessPermission, FormView):
    template_name = 'order/order-checkout.html'
    form_class = OrderCheckoutForm
    
    def form_valid(self, form):
        user = self.request.user
        cleaned_data = form.cleaned_data
        address = cleaned_data['address_id']
        copon = cleaned_data['copon']

        cart = CartModel.objects.get(user=user)
        order = self.create_order(address)
        
        self.create_order_items(cart, order)
        self.clear_cart(cart)

        total_price = order.calculate_total_price()
        self.apply_copon(copon, total_price, order, user)
        
        order.save()
        
        return redirect(reverse_lazy('order:order-success'))
        
    def form_invalid(self, form):
        return redirect(reverse_lazy('order:order-failed'))

    def apply_copon(self, copon, total_price, order, user):
        if copon:
            discunt_price = round(
                total_price * (
                    Decimal(copon.discount_percent / Decimal("100"))
                )
            )
            total_price -= discunt_price

            order.copon = copon
            copon.used_by.add(user)
            copon.save()
            
        order.total_price = total_price

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
            OrderItemsModel.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.get_price(),
        )
    
    def clear_cart(self, cart):
        cart.cart_items.all().delete()
        CartSession(self.request.session).clear()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['addresses'] = UserAddressModel.objects.filter(user=self.request.user)
        
        cart = get_cart(self.request)
        price = cart.get_total_payment_amount()
        total_tax = round(price * 10 / 100)
        context['price'] = price
        context['total_tax'] = total_tax
        context['total_price'] = price + total_tax
        
        return context
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
     
class OrderSuccessView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = 'order/success.html'


class OrderFailedView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = 'order/failed.html'
    
    
class ValidateCoponView(LoginRequiredMixin, HasCustomerAccessPermission, View):

    def post(self, *args, **kwargs):
        code = self.request.POST.get('code')
        user = self.request.user
        
        if not code:
            return JsonResponse({'message': 'کد تخفیف وارد نشده است'}, status=400)
        
        try:
            copon = CoponModel.objects.get(code=code)
        except CoponModel.DoesNotExist:
            return JsonResponse({"message": 'کد تخفیف یافت نشد'}, status=404)

        if copon.is_usage_limit_reached:
            return JsonResponse({"message": 'حد استفاده از کد تخفیف به اتمام رسیده است'}, status=403)
            
        if copon.expiration_date and copon.expiration_date < timezone.now():
            return JsonResponse({"message": 'کد تخفیف منقضی شده است'}, status=403)

        if copon.is_used_by(user):
            return JsonResponse({"message": 'این کد تخفیف قبلا توسط شما استفاده شده است'}, status=403)

        try:
            cart = CartModel.objects.get(user=user)
        except CartModel.DoesNotExist:
            return JsonResponse({"message": 'سبد خرید یافت نشد'}, status=404)


        total_price = cart.calculate_total_price()
        discount_percent = Decimal(copon.discount_percent) / Decimal('100')
        total_price = round(total_price - (total_price * discount_percent), 0)
        total_tax = round((total_price * Decimal("10")) / Decimal("100"), 0)

        return JsonResponse({
            'message': 'کد تخفیف با موفقیت ثبت شد',
            'total_tax': total_tax,
            'total_price': total_price,
        }, status=200)