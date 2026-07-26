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
        for item in self.cart_obj.cart_items.select_related('product').all():
            price = item.quantity * item.product.get_price()
            self.total_payment_price += price
            cart_items.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "total_price": price,
                "product_obj": item.product,
            })
        return cart_items

    def get_total_payment_amount(self):
        self.get_cart_items()
        return self.total_payment_price

    def add_product(self, product_id):
        item, created = CartItemModel.objects.get_or_create(
            cart=self.cart_obj,
            product_id=product_id,
            defaults={"quantity": 1}
        )
        if not created:
            item.quantity += 1
            item.save()

    def clear(self):
        self.cart_obj.cart_items.all().delete()


    def increase_quantity(self, product_id):
        item = self.cart_obj.cart_items.get(product_id=product_id)
        item.quantity += 1
        item.save()
        
    def decrease_quantity(self, product_id):
        item = self.cart_obj.cart_items.get(product_id=product_id)
        if item.quantity != 1:
            item.quantity -= 1
            item.save()

    def delete_product(self, product_id):
        self.cart_obj.cart_items.filter(product_id=product_id).delete()