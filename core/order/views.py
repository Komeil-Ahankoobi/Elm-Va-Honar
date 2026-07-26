from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from dashboard.permissions import HasCustomerAccessPermission
from cart.utils import get_cart

# Create your views here.
class OrderCheckoutView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = 'order/order-checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        total_price = cart.get_total_payment_amount()
        send_price = 15000
        context['total_price'] = total_price + send_price
        return context
    