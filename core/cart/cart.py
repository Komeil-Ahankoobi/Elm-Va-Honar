class CartSession:
    def __init__(self, session):
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








