# Shopping Cart System Documentation

## Overview
Session-based shopping cart system for CertiBuy marketplace. Products are stored in Django sessions, no database models needed.

## Features
- ✅ Add products to cart
- ✅ Remove items from cart  
- ✅ Update product quantities
- ✅ View cart with detailed breakdown
- ✅ Calculate totals and item counts
- ✅ Cart persistence using Django sessions
- ✅ Clear entire cart
- ✅ Real-time cart count in navbar

## Files Structure

### Backend
- **core/utils.py** - Cart class for session management
  - `add(product_id, quantity)` - Add product to cart
  - `remove(product_id)` - Remove product from cart
  - `update(product_id, quantity)` - Update quantity
  - `get_items()` - Get all cart items with product details
  - `get_total_price()` - Calculate total price
  - `get_total_items()` - Count total items
  - `clear()` - Empty the cart

- **core/views.py** - Cart views
  - `CartView` - Display cart page
  - `add_to_cart()` - POST endpoint to add items
  - `remove_from_cart()` - POST endpoint to remove items
  - `update_cart()` - POST endpoint to update quantities
  - `clear_cart()` - POST endpoint to clear cart

- **core/urls.py** - Cart URL routing
  - `/cart/` - View cart page
  - `/cart/add/` - Add to cart endpoint
  - `/cart/remove/` - Remove from cart endpoint
  - `/cart/update/` - Update quantity endpoint
  - `/cart/clear/` - Clear cart endpoint

### Frontend
- **templates/pages/cart.html** - Shopping cart page
  - Product list with images
  - Quantity updater
  - Remove buttons
  - Cart summary panel
  - Order total calculation

- **templates/pages/shop.html** - Updated with "Add to Cart" button
  - Form submission to add_to_cart view
  - CSRF token protection
  - Hidden quantity field (default 1)

- **templates/base.html** - Updated navbar
  - Cart link with item counter badge
  - Shows number of items in cart
  - Updates dynamically

## Session Storage Format

```python
{
    'cart': {
        '1': {
            'quantity': 2,
            'price': '1299.99'
        },
        '5': {
            'quantity': 1,
            'price': '399.99'
        }
    }
}
```

## Usage Flow

### 1. Add to Cart
```
User clicks "Add to Cart" on product
    ↓
POST to /cart/add/ with product_id
    ↓
Cart.add(product_id) updates session
    ↓
Message displayed + redirect to shop
```

### 2. View Cart
```
User clicks "Cart" in navbar
    ↓
GET /cart/
    ↓
CartView renders cart.html
    ↓
Fetches item details from database
    ↓
Calculates totals
```

### 3. Update Quantity
```
User changes quantity and clicks update
    ↓
POST to /cart/update/ with product_id & quantity
    ↓
Cart.update() modifies session
    ↓
Page refreshes to show new totals
```

### 4. Remove Item
```
User clicks "Remove"
    ↓
POST to /cart/remove/ with product_id
    ↓
Cart.remove() deletes from session
    ↓
Item disappears from cart
```

## Key Implementation Details

### Session Management
- Cart stored in `request.session['cart']`
- Product ID as key (string)
- Quantity and price stored as values
- `session.modified = True` to save changes

### Data Retrieval
- `get_items()` fetches fresh product data from DB
- Handles missing/deleted products gracefully
- Calculates line totals dynamically

### Price Calculation
- Stores price at purchase time in session
- Allows for price updates without affecting old carts
- Total = sum of (price × quantity) for all items

### CSRF Protection
- All POST forms include `{% csrf_token %}`
- Prevents cross-site attacks

### Error Handling
- Invalid product IDs removed automatically
- Quantity validation (min 1)
- Graceful handling of missing products

## URLs & Endpoints

| URL | Method | Purpose |
|-----|--------|---------|
| `/cart/` | GET | View shopping cart |
| `/cart/add/` | POST | Add product to cart |
| `/cart/remove/` | POST | Remove product from cart |
| `/cart/update/` | POST | Update product quantity |
| `/cart/clear/` | POST | Clear entire cart |

## Example Usage

### Add to Cart (from template)
```html
<form method="post" action="{% url 'core:add_to_cart' %}">
    {% csrf_token %}
    <input type="hidden" name="product_id" value="{{ product.id }}">
    <input type="hidden" name="quantity" value="1">
    <button type="submit">Add to Cart</button>
</form>
```

### Update Quantity (from cart page)
```html
<form method="post" action="{% url 'core:update_cart' %}">
    {% csrf_token %}
    <input type="hidden" name="product_id" value="{{ item.product.id }}">
    <input type="number" name="quantity" value="{{ item.quantity }}" min="1">
    <button type="submit">Update</button>
</form>
```

## Benefits of Session-Based Cart

1. **No Database** - No need for Order/CartItem models
2. **Privacy** - Cart data never stored on server
3. **Simple** - Easy to implement and maintain
4. **Fast** - Session middleware handles everything
5. **Flexible** - Easy to convert to orders when checking out

## Limitations & Future Improvements

Current Limitations:
- Cart cleared when session expires (default 2 weeks)
- No persistent cart across browsers
- No abandoned cart recovery

Future Enhancements:
- Database-backed cart for logged-in users
- Wishlist feature
- Cart persistence across devices
- Abandoned cart email reminders
- Coupon/discount system

## Testing the Cart

1. Go to /shop/ and click "Add to Cart" on a product
2. Check navbar - cart count should increase
3. Click "Cart" to view full cart page
4. Try updating quantities
5. Try removing items
6. Clear cart and verify empty state

## Technical Notes

- Cart uses string product IDs for session JSON compatibility
- Prices stored as strings to prevent float precision issues
- Product images and details fetched fresh from DB each view
- Session data persists across page navigation
- Cart can be tested with/without user login
