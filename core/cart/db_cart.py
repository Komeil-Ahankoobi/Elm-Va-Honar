from .models import CartModel, CartItemModel


class CartDB:
    def __init__(self, user):
        self.user = user
        self.cart_obj, created = CartModel.objects.get_or_create(user=user)
        self.total_payment_price = 0

    def get_total_quantity(self):
        total_quantity = 0
        for item in self.cart_obj.cart_items.all():
            total_quantity += item.quantity
        return total_quantity

    def get_cart_items(self):
        cart_items = []
        self.total_payment_price = 0
        for item in self.cart_obj.cart_items.select_related('product', 'variant').all():
            unit_price = item.variant.get_price() if item.variant else item.product.get_price()
            price = item.quantity * unit_price
            self.total_payment_price += price
            cart_items.append({
                "product_id": item.product_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "total_price": price,
                "product_obj": item.product,
                "variant_obj": item.variant,
            })
        return cart_items

    def get_total_payment_amount(self):
        self.get_cart_items()
        return self.total_payment_price

    def add_product(self, product_id, variant_id=None):
        item, created = CartItemModel.objects.get_or_create(
            cart=self.cart_obj,
            product_id=product_id,
            variant_id=variant_id,
            defaults={"quantity": 1}
        )
        if not created:
            item.quantity += 1
            item.save()

    def clear(self):
        self.cart_obj.cart_items.all().delete()


    def increase_quantity(self, product_id, variant_id=None):
        item = self.cart_obj.cart_items.get(product_id=product_id, variant_id=variant_id)
        item.quantity += 1
        item.save()
        
    def decrease_quantity(self, product_id, variant_id):
        item = self.cart_obj.cart_items.get(product_id=product_id, variant_id=variant_id)
        if item.quantity != 1:
            item.quantity -= 1
            item.save()

    def delete_product(self, product_id, variant_id):
        self.cart_obj.cart_items.filter(product_id=product_id, variant_id=variant_id).delete()