from shop.models import (
    ProductModel,
    ProductStatusType,
    ProductVarientModel
)


class CartSession:
    def __init__(self, session):
        self.total_payment_price = 0
        self.session = session
        cart = self.session.get("cart")
        if cart is None:
            cart = {"items": []}
            self.session["cart"] = cart
            self.session.modified = True
        self._cart = cart

    @staticmethod
    def _normalize(product_id, variant_id):
        return (
            int(product_id) if product_id is not None else None,
            int(variant_id) if variant_id else None,
        )

    @property
    def get_cart(self):
        return self._cart

    def get_total_quantity(self):
        total_quantity = 0
        for item in self._cart["items"]:
            total_quantity += item["quantity"]
        return total_quantity

    def get_cart_items(self):
        cart_items = []
        self.total_payment_price = 0
        for item in self._cart["items"]:
            product_obj = ProductModel.objects.filter(
                id=item["product_id"], status=ProductStatusType.publish.value
            ).first()
            if product_obj is None:
                continue

            variant_id = item.get("variant_id")
            price = item["quantity"] * product_obj.get_price()
            self.total_payment_price += price

            cart_items.append({
                "product_id": item["product_id"],
                "variant_id": variant_id,
                "quantity": item["quantity"],
                "total_price": price,
                "product_obj": product_obj,
                "variant_obj": (
                    ProductVarientModel.objects.filter(id=variant_id).first()
                    if variant_id else None
                ),
            })
        return cart_items

    def get_total_payment_amount(self):
        self.get_cart_items()
        return self.total_payment_price

    def add_product(self, product_id, variant_id=None):
        product_id, variant_id = self._normalize(product_id, variant_id)
        for item in self._cart["items"]:
            if product_id == item["product_id"] and variant_id == item.get("variant_id"):
                item["quantity"] += 1
                break
        else:
            self._cart["items"].append({
                "product_id": product_id,
                "variant_id": variant_id,
                "quantity": 1,
            })
        self.save()

    def clear(self):
        self._cart = self.session["cart"] = {"items": []}
        self.save()

    def save(self):
        self.session.modified = True

    def increase_quantity(self, product_id, variant_id=None):
        product_id, variant_id = self._normalize(product_id, variant_id)
        for item in self._cart["items"]:
            if product_id == item["product_id"] and variant_id == item.get("variant_id"):
                item["quantity"] += 1
                break
        self.save()

    def decrease_quantity(self, product_id, variant_id=None):
        product_id, variant_id = self._normalize(product_id, variant_id)
        for item in self._cart["items"]:
            if product_id == item["product_id"] and variant_id == item.get("variant_id"):
                if item["quantity"] > 1:
                    item["quantity"] -= 1
                break
        self.save()

    def delete_product(self, product_id, variant_id=None):
        product_id, variant_id = self._normalize(product_id, variant_id)
        self._cart["items"] = [
            item for item in self._cart["items"]
            if not (product_id == item["product_id"] and variant_id == item.get("variant_id"))
        ]
        self.save()
