# Cashify-Style Product Page - Quick Reference

## For Developers

### How to Add New Product Options

#### 1. Add New Condition Grade
**Template**: `templates/products/product_detail.html`

```html
<!-- Add new button to condition selector -->
<button type="button" class="selector-option" 
        data-condition="fair" 
        data-price="449.00" 
        data-description="Well-used but fully functional">
    <span class="option-label">Fair</span>
    <span class="option-price">$449</span>
</button>
```

#### 2. Add New Storage Option
```html
<!-- Add new button to storage selector -->
<button type="button" class="selector-option" 
        data-storage="512gb" 
        data-price-add="150">
    512GB <span class="price-add">+$150</span>
</button>
```

#### 3. Add New Color
```html
<!-- Add new color button -->
<button type="button" class="color-option" 
        data-color="Forest Green" 
        style="background: #134e48;">
</button>
```

### How Dynamic Pricing Works

```javascript
// Base price from condition
basePrice = 599.00 (Like New) | 549.00 (Excellent) | 499.00 (Good)

// Storage add-on
storageAddOn = 0 (64GB) | 50 (128GB) | 100 (256GB)

// Final price calculation
finalPrice = basePrice + storageAddOn

// Example: Like New + 256GB = $599 + $100 = $699
```

### Session Data Structure

```python
# Session data when user clicks Buy Now
request.session['buy_now_options'] = {
    'condition': 'likenew',    # User's selected condition
    'storage': '128gb',         # User's selected storage
    'color': 'Sapphire Blue',   # User's selected color
}
```

### How to Customize Combo Offers

**Template**: `templates/products/product_detail.html`

```html
<div class="combo-card">
    <div class="combo-images">
        <!-- Main product image -->
        <img src="{{ product.images.first.image.url }}" alt="Main">
        <span class="plus-icon">+</span>
        <!-- Accessory image -->
        <img src="{% static 'images/accessories/charger.jpg' %}" alt="Accessory">
    </div>
    <h5 class="combo-title">Your Combo Title</h5>
    <p class="combo-price">
        Combo Price: <strong>$649</strong> 
        <span class="strike">$699</span>
    </p>
    <button class="btn btn-sm btn-outline-primary w-100">Add Combo to Cart</button>
</div>
```

## For Content Managers

### Setting Product Prices

1. **Base Prices** (set in database):
   - Product model: `price` field
   
2. **Condition Variations** (set in template):
   - Like New: Usually highest price
   - Excellent: 8-10% discount
   - Good: 15-20% discount

3. **Storage Add-Ons** (set in template):
   - 64GB: Base (no add-on)
   - 128GB: +$50 typical
   - 256GB: +$100 typical
   - 512GB: +$150 typical

### Product Images Guidelines

**Thumbnail Gallery**:
- Minimum: 3 images
- Recommended: 5-8 images
- Size: 1200x1200px (square)
- Format: JPG or PNG
- File size: < 500KB per image

**Image Order**:
1. Front view
2. Back view
3. Side angles
4. Close-ups of key features
5. Condition/cosmetic details
6. Accessories included

## For Users (Customer-Facing)

### How to Purchase

1. **Select Condition**:
   - Like New: Looks brand new, no visible wear
   - Excellent: Minimal signs of use
   - Good: Visible wear but fully functional

2. **Choose Storage**:
   - Select based on your needs
   - Price updates automatically

3. **Pick Color**:
   - Click color circle
   - Selected color shown in text

4. **Check Delivery**:
   - Enter 6-digit pincode
   - Click "Check" for delivery estimate

5. **Add to Cart or Buy Now**:
   - Add to Cart: Continue shopping
   - Buy Now: Direct checkout

### Understanding Prices

**Example Product Pricing**:
```
Base Product: Refurbished iPhone 12

Condition Options:
├─ Like New: $599
├─ Excellent: $549
└─ Good: $499

Storage Add-Ons:
├─ 64GB:  +$0
├─ 128GB: +$50
└─ 256GB: +$100

Final Price Examples:
├─ Like New + 64GB  = $599
├─ Excellent + 128GB = $599 ($549 + $50)
└─ Good + 256GB     = $599 ($499 + $100)
```

## CSS Customization

### Changing Primary Colors

```css
/* Main theme colors */
.cashify-product-detail {
    --primary-blue: #2563eb;    /* Change brand color */
    --success-green: #16a34a;   /* Change success color */
    --text-primary: #1e293b;    /* Change heading color */
}
```

### Button Styles

```css
/* Primary button (Buy Now) */
.btn-primary {
    background: #2563eb;
    border-color: #2563eb;
    font-weight: 600;
}

/* Outline button (Add to Cart) */
.btn-outline-primary {
    border: 1px solid #2563eb;
    color: #2563eb;
}
```

### Selector Option Styles

```css
/* Active state for selectors */
.selector-option.active {
    border-color: #2563eb;
    background: #eff6ff;
    color: #2563eb;
}

/* Hover effect */
.selector-option:hover {
    border-color: #2563eb;
}
```

## JavaScript Event Reference

### Available Events

```javascript
// Condition selection change
document.querySelector('.condition-selector').addEventListener('change', ...)

// Storage selection change
document.querySelector('.storage-selector').addEventListener('change', ...)

// Color selection change
document.querySelector('.color-selector').addEventListener('change', ...)

// Price update
window.addEventListener('priceUpdate', ...)

// Thumbnail click
document.querySelectorAll('.thumb-btn').forEach(btn => 
    btn.addEventListener('click', ...)
)
```

### Custom Event Dispatching

```javascript
// Dispatch custom event when price updates
function updatePrice() {
    const total = basePrice + storageAddOn;
    // ... update price display ...
    
    // Dispatch event for tracking
    window.dispatchEvent(new CustomEvent('priceUpdate', {
        detail: { price: total, condition: selectedCondition }
    }));
}
```

## Troubleshooting

### Price Not Updating
**Check**:
1. JavaScript loaded without errors (check browser console)
2. `data-price` and `data-price-add` attributes set correctly
3. `updatePrice()` function is defined

### Images Not Switching
**Check**:
1. `data-image` attribute has correct URL
2. Image files exist and are accessible
3. JavaScript thumb click handler is attached

### Options Not Saving to Session
**Check**:
1. Hidden form fields have correct IDs
2. Form submits successfully (check network tab)
3. Session middleware is enabled

### Sticky Bar Not Appearing
**Check**:
1. `.sticky-buy-trigger` class exists on Buy Now button
2. `#stickyBuyBar` element exists
3. Scroll event listener is attached

## API Integration (Future)

### Expected Endpoint Structure

```javascript
// GET product options and pricing
GET /api/products/{id}/options/
Response: {
    conditions: [
        { value: 'likenew', label: 'Like New', price: 599.00 },
        { value: 'excellent', label: 'Excellent', price: 549.00 }
    ],
    storage: [
        { value: '64gb', label: '64GB', priceAdd: 0 },
        { value: '128gb', label: '128GB', priceAdd: 50 }
    ],
    colors: [
        { value: 'black', label: 'Midnight Black', hex: '#000000' }
    ]
}

// POST validate options and get final price
POST /api/products/{id}/validate-options/
Body: {
    condition: 'likenew',
    storage: '128gb',
    color: 'black'
}
Response: {
    valid: true,
    finalPrice: 649.00,
    available: true
}
```

## Performance Tips

1. **Lazy Load Images**: Use `loading="lazy"` on images below fold
2. **Optimize Thumbnails**: Create 80x80px thumbnails separately
3. **Minify JavaScript**: Use minified version in production
4. **Cache Bust Static Files**: Version CSS/JS files
5. **CDN for Font Awesome**: Use CDN instead of local files

## Accessibility Checklist

- [ ] All images have alt text
- [ ] Buttons have descriptive labels
- [ ] Color selectors have text alternatives
- [ ] Form inputs have labels
- [ ] Tab navigation works correctly
- [ ] Screen reader friendly
- [ ] Keyboard shortcuts work
- [ ] Focus indicators visible

---

**Need Help?**
- Check browser console for JavaScript errors
- Verify Django debug mode for server errors
- Review network tab for API failures
- Test in incognito mode to rule out cache issues
