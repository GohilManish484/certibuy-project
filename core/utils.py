from products.models import Product
from orders.models import WarrantyPlan

class Cart:
    """Session-based shopping cart management"""
    
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
    
    def add(self, product_id, quantity=1, warranty_plan_id=None):
        """Add product to cart or increase quantity"""
        product_id = str(product_id)
        if product_id not in self.cart:
            product = Product.objects.get(id=product_id)
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price),
                'warranty_plan_id': None,
                'warranty_price': '0.00'
            }
        self.cart[product_id]['quantity'] += int(quantity)
        
        # Handle warranty plan
        if warranty_plan_id:
            try:
                warranty_plan = WarrantyPlan.objects.get(id=warranty_plan_id, is_active=True)
                self.cart[product_id]['warranty_plan_id'] = str(warranty_plan_id)
                self.cart[product_id]['warranty_price'] = str(warranty_plan.price)
            except WarrantyPlan.DoesNotExist:
                pass
        
        self.save()
    
    def remove(self, product_id):
        """Remove product from cart"""
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def update(self, product_id, quantity):
        """Update product quantity"""
        product_id = str(product_id)
        quantity = int(quantity)
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.remove(product_id)
            self.save()
    
    def save(self):
        """Mark session as modified"""
        self.session['cart_count'] = self.get_total_items()
        self.session.modified = True
    
    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        """Get total price of cart including warranties"""
        total = 0
        for item in self.cart.values():
            item_total = float(item['price']) * item['quantity']
            warranty_total = float(item.get('warranty_price', 0)) * item['quantity']
            total += item_total + warranty_total
        return round(total, 2)
    
    def get_items(self):
        """Get cart items with product details and warranty"""
        items = []
        for product_id, item in self.cart.items():
            try:
                product = Product.objects.get(id=product_id)
                warranty_plan = None
                if item.get('warranty_plan_id'):
                    try:
                        warranty_plan = WarrantyPlan.objects.get(id=item['warranty_plan_id'])
                    except WarrantyPlan.DoesNotExist:
                        pass
                
                items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'price': float(item['price']),
                    'warranty_plan': warranty_plan,
                    'warranty_price': float(item.get('warranty_price', 0)),
                    'total_price': round(
                        (float(item['price']) + float(item.get('warranty_price', 0))) * item['quantity'], 
                        2
                    )
                })
            except Product.DoesNotExist:
                self.remove(product_id)
        return items
    
    def clear(self):
        """Clear all items from cart"""
        self.session['cart'] = {}
        self.save()
    
    def __len__(self):
        """Return number of unique items"""
        return len(self.cart)
