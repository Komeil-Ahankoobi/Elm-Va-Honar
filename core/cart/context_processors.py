from .utils import get_cart

def cart_processor(request):
    cart = get_cart(request)
    return {'cart': cart}

