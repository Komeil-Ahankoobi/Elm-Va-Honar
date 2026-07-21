from django.db.models import F, DecimalField, ExpressionWrapper
from django.db.models.functions import Round
from django.core.exceptions import FieldError

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
    paginate_by = 6

    def get_queryset(self):
        queryset = ProductModel.objects.filter(
            status=ProductStatusType.publish.value
        ).annotate(
            final_price=Round(ExpressionWrapper(
                 F("price") - (F("price") * F("discount_percent") / 100),
                 output_field=DecimalField()
            ))
        )
        
        
        if q := self.request.GET.get('q'):
            queryset = queryset.filter(title__icontains=q)        
        try:
            if min_price := self.request.GET.get('min_price'):
                min_price = int(min_price)
                queryset = queryset.filter(final_price__gte=min_price)
        except (ValueError, TypeError):
            pass 
        try:
            if max_price := self.request.GET.get('max_price'):
                max_price = int(max_price)
                queryset = queryset.filter(final_price__lte=max_price)
        except (ValueError, TypeError):
            pass
        
        filter_by = self.request.GET.get('filter-by')
        
        if filter_by == 'cheep_to_exp':
            queryset = queryset.order_by('final_price')        
        elif filter_by == 'exp_to_cheep':
            queryset = queryset.order_by('-final_price')        
        elif filter_by == 'new':
            queryset = queryset.order_by('-created_date')
        
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_product'] = self.object_list.count()
        context['categories'] = ProductCategoryModel.objects.all()
        
        context['filter_by'] = self.request.GET.get('filter-by')

        return context
    

class ShopProductDetailView(DetailView):
    template_name = "shop/product-detail.html"
    queryset = ProductModel.objects.filter(
        status=ProductStatusType.publish.value) 