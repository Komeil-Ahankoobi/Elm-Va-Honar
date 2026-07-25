from .cart import CartSession
from .db_cart import CartDB


def get_cart(request):
    if request.user.is_authenticated:
        return CartDB(request.user)
    return CartSession(request.session)