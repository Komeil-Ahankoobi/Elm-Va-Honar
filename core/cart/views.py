from django.views.generic import View
from django.views.generic import TemplateView
from django.http import JsonResponse
import json

from .utils import get_cart


class SessionAddProduct(View):

    def post(self, request, *args, **kwargs):
        cart = get_cart(request)
        data = json.loads(request.body)
        product_id = data.get('product_id')
        if product_id:
            cart.add_product(product_id)
        return JsonResponse({
            'total_quantity': cart.get_total_quantity(),
        })


class SessionCartSummary(TemplateView):
    template_name = "cart/cart-summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        context["cart_items"] = cart.get_cart_items()
        return context
class UpdateCartQuantity(View):

    def post(self, request, *args, **kwargs):
        cart = get_cart(request)
        data = json.loads(request.body)
        product_id = data.get('product_id')
        action = data.get("action")

        if action == "inc":
            cart.increase_quantity(product_id)
        elif action == "dec":
            cart.decrease_quantity(product_id)

        cart_items = cart.get_cart_items()

        updated_item = None
        for item in cart_items:
            if item["product_id"] == int(product_id):
                updated_item = item
                break

        if updated_item:
            item_quantity = updated_item["quantity"]
            item_total_price = updated_item["total_price"]
        else:
            item_quantity = 0
            item_total_price = 0

        return JsonResponse({
            'quantity': item_quantity,
            'item_total_price': item_total_price,
            'cart_total_price': cart.get_total_payment_amount(),
            'total_quantity': cart.get_total_quantity(),
        })



class DeleteProduct(View):

    def post(self, request, *args, **kwargs):
        cart = get_cart(request)
        data = json.loads(request.body)
        product_id = data.get("product_id")
        if product_id:
            cart.delete_product(product_id)
        return JsonResponse({
            "cart_total_price":cart.get_total_payment_amount(),
            "total_quantity":cart.get_total_quantity()
        })


