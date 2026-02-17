from django import forms
from .models import Inspection

class InspectionForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ['inspector', 'inspection_date', 'condition_grade', 'inspection_notes', 'status']
        widgets = {
            'inspector': forms.Select(attrs={'class': 'form-control'}),
            'inspection_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'condition_grade': forms.Select(attrs={'class': 'form-control'}),
            'inspection_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
