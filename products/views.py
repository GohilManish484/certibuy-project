from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Product
from orders.models import WarrantyPlan

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(certification_status='certified').prefetch_related('images')
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        # Fetch the product's inspection if it exists
        if product.inspection:
            context['inspection'] = product.inspection
        # Fetch active warranty plans
        if product.is_warranty_available:
            context['warranty_plans'] = WarrantyPlan.objects.filter(is_active=True)
        return context
