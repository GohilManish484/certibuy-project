from django.db import models
from django.conf import settings
from core.validators import validate_image_file, validate_image_content_type, secure_filename


def submission_image_upload_path(instance, filename):
    """Generate secure upload path for submission images"""
    secure_name = secure_filename(filename)
    return f'submissions/{instance.submission.seller.id}/{secure_name}'


class SellerSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('inspection_scheduled', 'Inspection Scheduled'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    condition = models.CharField(max_length=50)
    expected_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product_name} - {self.seller.username}"

class SubmissionImage(models.Model):
    submission = models.ForeignKey(SellerSubmission, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to=submission_image_upload_path,
        validators=[validate_image_file, validate_image_content_type]
    )
    
    def __str__(self):
        return f"{self.submission.product_name} - Image"
