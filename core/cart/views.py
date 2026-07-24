from django.views.generic import View
from django.http import JsonResponse
import json

from .cart import CartSession

# Create your views here.
class SessionAddProduct(View):
    
    def post(self, request, *args, **kwargs):
        cart = CartSession(request.session)
        data = json.loads(request.body)
        product_id = data.get('product_id')
        if product_id:
            cart.add_product(product_id)
        return JsonResponse({'cart': cart.get_cart()})