from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'image_preview']
    readonly_fields = ['image_preview']
    verbose_name = "Product Image"
    verbose_name_plural = "Product Images"
    
    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px; border-radius: 4px;"/>', obj.image.url)
        return "No image uploaded yet"
    image_preview.short_description = 'Preview'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'condition_grade', 'stock_quantity', 'certification_status', 'created_at']
    list_filter = ['certification_status', 'condition_grade', 'category', 'created_at']
    search_fields = ['name', 'description', 'category']
    list_editable = ['certification_status']
    readonly_fields = ['created_at']
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'category',
                'price',
                'condition_grade',
            ),
            'classes': ('wide',),
        }),
        ('Product Details', {
            'fields': (
                'description',
                'warranty_info',
                'default_warranty_months',
                'is_warranty_available',
            ),
            'classes': ('wide',),
        }),
        ('Inventory Management', {
            'fields': (
                'stock_quantity',
                'low_stock_threshold',
            ),
            'classes': ('wide',),
        }),
        ('Certification & Inspection', {
            'fields': (
                'certification_status',
                'inspection',
                'created_at',
            ),
            'classes': ('wide',),
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('images')
    
    def save_model(self, request, obj, form, change):
        """Save the product and ensure all data is persisted"""
        super().save_model(request, obj, form, change)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'image_preview']
    list_filter = ['product']
    search_fields = ['product__name']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px; border-radius: 8px;"/>', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image Preview'
