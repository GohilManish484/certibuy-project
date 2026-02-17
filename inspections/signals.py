from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Inspection
from products.models import Product, ProductImage
from sellers.models import SubmissionImage

@receiver(post_save, sender=Inspection)
def create_product_on_approval(sender, instance, created, update_fields, **kwargs):
    """Create a certified product when inspection is approved"""
    # Only proceed if status changed to 'approved'
    if instance.status == 'approved':
        # Check if product already exists for this submission
        existing_product = Product.objects.filter(
            name=instance.submission.product_name,
            category=instance.submission.category
        ).first()
        
        if not existing_product:
            try:
                # Create the product with certified status
                product = Product.objects.create(
                    name=instance.submission.product_name,
                    category=instance.submission.category,
                    price=instance.submission.expected_price,
                    condition_grade=instance.condition_grade,
                    description=instance.submission.description,
                    certification_status='certified',
                    warranty_info=f"Inspected on {instance.inspection_date.strftime('%Y-%m-%d')} by inspector #{instance.inspector.id}",
                    inspection=instance
                )
                
                # Copy images from submission to product
                submission_images = SubmissionImage.objects.filter(submission=instance.submission)
                for sub_img in submission_images:
                    ProductImage.objects.create(
                        product=product,
                        image=sub_img.image
                    )
                
                # Update submission status to approved
                instance.submission.status = 'approved'
                instance.submission.save()
            except Exception as e:
                # Log error but don't break the signal
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error creating product for inspection {instance.id}: {str(e)}")
