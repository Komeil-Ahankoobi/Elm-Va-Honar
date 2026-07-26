from shop.models import ProductModel, ProductStatusType


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
        
    
    @property
    def get_cart(self):
        return self._cart

    def get_total_quantity(self):
        total_quantity = 0
        for item in self.get_cart["items"]:
            total_quantity += item["quantity"]
        return total_quantity

    def get_cart_items(self):
        cart_items = self._cart["items"]
        self.total_payment_price = 0
        for item in cart_items:
            product_obj = ProductModel.objects.get(id=item["product_id"], status=ProductStatusType.publish.value)
            price = item["quantity"] * product_obj.get_price()
            item["total_price"] = price
            self.total_payment_price += price
            item["product_obj"] = product_obj
        return cart_items

    def get_total_payment_amount(self):
        self.get_cart_items()
        return self.total_payment_price
        
        
    def add_product(self, product_id):
        for item in self._cart["items"]:
            if product_id == item['product_id']:
                item["quantity"] += 1
                break
        else:
            new_product = {
                "product_id": product_id,
                "quantity": 1
            }
            self._cart['items'].append(new_product)
        self.save()
    

    def clear(self):
        self._cart = self.session['cart'] = {'items': []}
        self.save()
    
    def save(self):
        self.session.modified = True

    def increase_quantity(self, product_id):
        for item in self._cart["items"]:
            if product_id == item["product_id"]:
                item["quantity"] += 1
                break
        self.save()
        
    def decrease_quantity(self, product_id):
        for item in self._cart["items"]:
            if product_id == item["product_id"]:
                if item["quantity"] != 1:    
                    item["quantity"] -= 1
                    break
                else:
                    break
        self.save()

    def delete_product(self, product_id):
        filtered_items = []
        for item in self._cart["items"]:
            if product_id != item["product_id"]:
                filtered_items.append(item)

        self._cart["items"] = filtered_items
        self.save()
                




    






