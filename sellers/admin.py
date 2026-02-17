from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import SellerSubmission, SubmissionImage

class SubmissionImageInline(admin.TabularInline):
    model = SubmissionImage
    extra = 0
    fields = ['image']
    readonly_fields = ['image']

@admin.register(SellerSubmission)
class SellerSubmissionAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'seller', 'category', 'expected_price', 'status', 'created_at', 'action_links']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['product_name', 'description', 'seller__username', 'seller__email']
    list_editable = ['status']
    readonly_fields = ['seller', 'created_at']
    inlines = [SubmissionImageInline]
    
    fieldsets = (
        ('Seller Information', {
            'fields': ('seller', 'created_at')
        }),
        ('Product Details', {
            'fields': ('product_name', 'category', 'condition', 'expected_price', 'description')
        }),
        ('Approval', {
            'fields': ('status', 'rejection_reason'),
            'classes': ('wide',)
        }),
    )
    
    actions = ['approve_submissions', 'schedule_inspection', 'reject_submissions']
    
    def action_links(self, obj):
        inspect_url = reverse('inspections:create', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="padding: 5px 10px; background: #2563eb; color: white; border-radius: 4px; text-decoration: none;">Schedule Inspection</a>',
            inspect_url
        )
    action_links.short_description = 'Actions'
    
    def approve_submissions(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} submissions approved.')
    approve_submissions.short_description = 'Approve selected submissions'
    
    def schedule_inspection(self, request, queryset):
        updated = queryset.update(status='inspection_scheduled')
        self.message_user(request, f'{updated} inspections scheduled.')
    schedule_inspection.short_description = 'Schedule inspection for selected'
    
    def reject_submissions(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} submissions rejected.')
    reject_submissions.short_description = 'Reject selected submissions'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('seller').prefetch_related('images')

@admin.register(SubmissionImage)
class SubmissionImageAdmin(admin.ModelAdmin):
    list_display = ['submission', 'image']
    list_filter = ['submission__status']
    search_fields = ['submission__product_name']
