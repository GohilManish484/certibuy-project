from django import forms
from .models import SellerSubmission

class SellerSubmissionForm(forms.ModelForm):
    class Meta:
        model = SellerSubmission
        fields = ['product_name', 'category', 'condition', 'expected_price', 'description']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
            'condition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., New, Excellent, Good'}),
            'expected_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Expected Price'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your product...'}),
        }
