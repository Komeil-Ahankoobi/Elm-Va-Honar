from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .cart import CartSession
from .models import CartModel, CartItemModel


@receiver(user_logged_in)
def merge_session_cart_to_db(sender, request, user, **kwargs):
    session_cart = CartSession(request.session)
    items = session_cart.get_cart["items"]

    if not items:
        return

    cart_obj, created = CartModel.objects.get_or_create(user=user)

    for item in items:
        cart_item, created = CartItemModel.objects.get_or_create(
            cart=cart_obj,
            product_id=item["product_id"],
            defaults={"quantity": item["quantity"]}
        )
        if not created:
            cart_item.quantity += item["quantity"]
            cart_item.save()

    session_cart.clear()