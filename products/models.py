from django.db import models
from django.urls import reverse
from django.conf import settings
from core.validators import validate_image_file, validate_image_content_type, secure_filename


def product_image_upload_path(instance, filename):
    """Generate secure upload path for product images"""
    secure_name = secure_filename(filename)
    product_id = instance.product.id if instance.product.id else 'temp'
    return f'products/{product_id}/{secure_name}'


class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
    ]
    
    CERTIFICATION_CHOICES = [
        ('pending', 'Pending'),
        ('certified', 'Certified'),
        ('rejected', 'Rejected'),
    ]
    
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition_grade = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    description = models.TextField()
    warranty_info = models.TextField(blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    certification_status = models.CharField(max_length=20, choices=CERTIFICATION_CHOICES, default='pending')
    default_warranty_months = models.PositiveIntegerField(default=6)
    is_warranty_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    inspection = models.OneToOneField('inspections.Inspection', on_delete=models.SET_NULL, null=True, blank=True, related_name='product')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'pk': self.pk})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to=product_image_upload_path,
        validators=[validate_image_file, validate_image_content_type]
    )
    
    def __str__(self):
        return f"{self.product.name} - Image"

