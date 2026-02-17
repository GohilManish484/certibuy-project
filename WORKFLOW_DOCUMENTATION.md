# CertiBuy Product Workflow Documentation

## Complete Product Lifecycle: From Submission to Shop Display

### Step 1: Seller Submits Product
- **Action**: Seller goes to `/sellers/submit/` and fills out the product submission form
- **Model**: `SellerSubmission` is created with `status='pending'`
- **Includes**: Product name, category, price, description, condition, images
- **Visibility**: NOT visible on shop page yet
- **Status**: Awaiting inspection

### Step 2: Inspection Team Reviews
- **Action**: Inspector goes to Django admin → Inspections → Create new inspection record
- **Model**: `Inspection` is created for the `SellerSubmission`
- **Inspector**: Selects inspector user, inspection date, condition grade, inspection notes
- **Initial Status**: `pending`

### Step 3: Inspector Approves/Rejects
- **Action**: Inspector sets `Inspection.status` to `approved` or `rejected`
  - Via admin list edit (list_editable checkbox)
  - Via bulk action "Approve selected inspections"
  - Via detail page
- **If Approved**:
  - ✅ Django signal triggers automatically
  - ✅ Product is created with `certification_status='certified'`
  - ✅ Product images are copied from submission
  - ✅ Product appears on shop page instantly
- **If Rejected**:
  - ❌ Product NOT created
  - ❌ SellerSubmission updated to `status='rejected'`
  - ❌ Product does NOT appear on shop

### Step 4: Certified Product on Shop
- **URL**: `/shop/`
- **Filter**: Only products with `certification_status='certified'` are displayed
- **Badge**: Shows "✓ Certified" badge on product card
- **Condition**: Shows inspection grade (new, excellent, good, fair)
- **Features**: Search, category filter, condition filter, price range filter, pagination

---

## Database Models

### SellerSubmission
- Status: `pending` → `approved` or `rejected`
- NOT directly visible on shop
- Linked to Inspection for review

### Inspection
- Status: `pending` → `completed` → `approved` or `rejected`
- When status='approved': Product created automatically via signal

### Product
- `certification_status`: Only 'certified' products appear on shop
- `certification_status` values:
  - `pending`: Not yet reviewed
  - `certified`: Approved by inspector, visible on shop ✅
  - `rejected`: Rejected by inspector, hidden from shop
  - Can be manually set via admin

---

## Signal Flow

```
Inspector updates Inspection.status to 'approved'
        ↓
Django post_save signal fires
        ↓
Check if Product exists for this submission
        ↓
Create Product with certification_status='certified'
        ↓
Copy images from SellerSubmission to Product
        ↓
Update SellerSubmission.status to 'approved'
        ↓
Product appears on shop page immediately
```

---

## Admin Actions

### Inspection Admin
- **List View**: See all submissions pending inspection
- **Bulk Actions**:
  - "Approve selected inspections" → Creates products
  - "Reject selected inspections" → Marks rejected
  - "Mark as completed" → Changes status to completed
- **Line Edit**: Click status field to change directly

### Product Admin
- **List View**: See all products (certified and others)
- **Filter**: By certification_status to see only 'certified'
- **Edit**: Can manually change certification_status if needed

---

## Testing the Workflow

### Test Case 1: Full Approval Workflow
1. Login as seller → Go to /sellers/submit/ → Submit product
2. Login as admin → Go to admin → Inspections → Create inspection
3. Set status to 'approved' and save
4. Go to /shop/ → Product appears with "✓ Certified" badge ✅

### Test Case 2: Rejection Workflow
1. Same steps but set Inspection.status to 'rejected'
2. Go to /shop/ → Product does NOT appear ✅

### Test Case 3: Filter Only Shows Certified
1. Go to /shop/
2. All visible products have "✓ Certified" badge ✅
3. Only certification_status='certified' products are displayed ✅

---

## Important Notes

- **Sample Products**: The 12 sample electronic products were created directly as 'certified' for demo purposes. They bypass the normal inspection workflow.
- **Real Workflow**: When sellers submit products, they go through the inspection workflow described above.
- **Shop Page**: Only shows products where `certification_status='certified'`
- **Pending Products**: Sellers can view their submissions in `/sellers/my-submissions/` but they don't appear on shop page until approved.

---

## URLs and Admin Paths

- **Shop Page**: `/shop/` - Shows only certified products
- **Seller Submissions**: `/sellers/submit/` - Sellers submit products
- **View Submissions**: `/sellers/my-submissions/` - Seller sees their submissions
- **Inspection List**: `/inspections/` - Inspectors see pending inspections (staff only)
- **Admin Panel**: `/admin/` - Manage inspections and products
- **Product Admin**: `/admin/products/product/` - View/edit all products
- **Inspection Admin**: `/admin/inspections/inspection/` - Approve/reject submissions
