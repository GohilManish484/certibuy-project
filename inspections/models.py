from django.db import models
from django.conf import settings
from sellers.models import SellerSubmission

class Inspection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    submission = models.ForeignKey(SellerSubmission, on_delete=models.CASCADE, related_name='inspections')
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='inspections',
        limit_choices_to={'role': 'inspector'}
    )
    inspection_date = models.DateTimeField()
    condition_grade = models.CharField(max_length=20, choices=[
        ('new', 'New'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
    ])
    inspection_notes = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Inspection #{self.id} - {self.submission.product_name}"
