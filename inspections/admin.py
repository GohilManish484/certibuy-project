from django.contrib import admin
from .models import Inspection
from sellers.models import SellerSubmission

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'submission', 'inspector', 'inspection_date', 'condition_grade', 'status', 'created_at']
    list_filter = ['status', 'condition_grade', 'inspection_date', 'created_at']
    search_fields = ['submission__product_name', 'inspector__username', 'inspection_notes']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['submission', 'inspector']
    
    fieldsets = (
        ('Inspection Details', {
            'fields': ('submission', 'inspector', 'inspection_date')
        }),
        ('Assessment', {
            'fields': ('condition_grade', 'inspection_notes', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('submission', 'inspector')
    
    actions = ['approve_inspections', 'reject_inspections', 'mark_completed']
    
    def approve_inspections(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} inspections approved and products created.")
    approve_inspections.short_description = "Approve selected inspections"
    
    def reject_inspections(self, request, queryset):
        queryset.update(status='rejected')
        for inspection in queryset:
            inspection.submission.status = 'rejected'
            inspection.submission.save()
        self.message_user(request, f"{queryset.count()} inspections rejected.")
    reject_inspections.short_description = "Reject selected inspections"
    
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} inspections marked as completed.")
    mark_completed.short_description = "Mark as completed"
