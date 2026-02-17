# Inspection Workflow System

## Overview
Automated inspection workflow that creates products when inspections are approved.

## Models

### Inspection
- `submission`: ForeignKey to SellerSubmission
- `inspector`: ForeignKey to User (role=inspector)
- `inspection_date`: DateTime
- `condition_grade`: Choice (new, excellent, good, fair)
- `inspection_notes`: TextField
- `status`: Choice (pending, completed, approved, rejected)

## Workflow

1. **Staff creates inspection** for a seller submission
2. **Inspector assigned** to review the product
3. **When status = "approved"**:
   - Django signal triggers automatically
   - Product created with submission data
   - Images copied from submission to product
   - Submission status updated to "approved"
   - Product certification_status set to "certified"

## Signal Implementation

Located in `inspections/signals.py`:
- Uses `@receiver(post_save, sender=Inspection)`
- Checks if `status == 'approved'`
- Prevents duplicate products
- Copies all submission data and images

## Admin Features

### Inspection Admin
- List view with filters
- Bulk actions: approve, reject, mark completed
- Inline submission details
- Search by product name, inspector

### Seller Submission Admin
- "Schedule Inspection" button for each submission
- Direct link to create inspection form
- Status tracking

## URLs

- `/inspections/` - List all inspections (staff/inspectors only)
- `/inspections/<id>/` - Inspection detail view
- `/inspections/create/<submission_id>/` - Create new inspection

## Access Control

- **Staff**: Full access to all inspections
- **Inspectors**: Can view their assigned inspections
- **Sellers**: Cannot access inspection views

## Test Data

Run to create test inspector:
```bash
python manage.py create_inspector
```

Credentials:
- Username: `inspector1`
- Password: `inspector123`

## Automatic Product Creation

When inspection approved:
1. Product name = submission.product_name
2. Category = submission.category
3. Price = submission.expected_price
4. Condition = inspection.condition_grade
5. Description = submission.description
6. Certification = "certified"
7. Warranty info includes inspection date and inspector

Images automatically copied from SubmissionImage to ProductImage.
