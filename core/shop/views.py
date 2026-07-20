from django.shortcuts import render
from .models import (
    ProductModel, 
    ProductStatusType,
    ProductCategoryModel
)
from django.views.generic import (
    ListView,
    DetailView
)

class ShopProductView(ListView):
    template_name = "shop/shop.html"
    context_object_name = "products"
    paginate_by = 9

    def get_queryset(self):
        queryset = ProductModel.objects.filter(
            status=ProductStatusType.publish.value
        )
        
        if q := self.request.GET.get('q'):
            queryset = queryset.filter(title__icontains=q)        
        if min_price := self.request.GET.get('min_price'):
            queryset = queryset.filter(price__gte=min_price)        
        if max_price := self.request.GET.get('max_price'):
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_product'] = self.get_queryset().count()
        context['categories'] = ProductCategoryModel.objects.all()
        
        return context
    

class ShopProductDetailView(DetailView):
    template_name = "shop/product-detail.html"
    queryset = ProductModel.objects.filter(
        status=ProductStatusType.publish.value) 