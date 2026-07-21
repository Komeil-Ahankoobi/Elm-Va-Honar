from django.views.generic import (
    TemplateView,
    ListView,
    DetailView
)
from django.db.models import F, DecimalField, ExpressionWrapper
from django.db.models.functions import Round
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView

from ..permissions import HasAdminAccessPermission
from .forms import AdminPasswordChangeForm
from shop.models import (
    ProductModel,
    ProductStatusType,
    ProductCategoryModel
)


class AdminDashboardHomeView(HasAdminAccessPermission,TemplateView):
    template_name = 'dashboard/admin/main/main.html'
    
    
class AdminSecurityEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, PasswordChangeView):
    template_name = 'dashboard/admin/settings/settings.html'
    form_class = AdminPasswordChangeForm
    success_url = reverse_lazy("dashboard:admin:security-edit")
    success_message = 'رمز با موفقیت عوض شد'
    
    
class AdminOrdersView(TemplateView):
    template_name = 'dashboard/admin/orders/orders.html'


class AdminOrdersDetailView(DetailView):
    template_name = 'dashboard/admin/orders/orders-detail.html'


class AdminProductsListView(LoginRequiredMixin, HasAdminAccessPermission, ListView):
    template_name = 'dashboard/admin/products/products.html'
    context_object_name = "products"
    paginate_by = 9

    def get_queryset(self):
        queryset = ProductModel.objects.all().annotate(
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


class AdminEditProductsView(TemplateView):
    template_name = 'dashboard/admin/products/edit-products.html'


class AdminCustomersView(TemplateView):
    template_name = 'dashboard/admin/customers/customers.html'



