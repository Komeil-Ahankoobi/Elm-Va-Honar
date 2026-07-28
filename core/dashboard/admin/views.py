from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    UpdateView,
    CreateView,
    DeleteView
)
from django.db.models import F, DecimalField, ExpressionWrapper
from django.db.models.functions import Round
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
import jdatetime
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.models import User

from ..permissions import HasAdminAccessPermission
from .forms import (
    AdminPasswordChangeForm,
    AdminProductDetailEditFrom,
)
from shop.models import (
    ProductModel,
    ProductCategoryModel
)
from order.models import (
    OrderModel,
    OrderStatusType
)


class AdminDashboardHomeView(HasAdminAccessPermission,TemplateView):
    template_name = 'dashboard/admin/main/main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        now = timezone.now()
        today_jalai = jdatetime.datetime.fromgregorian(datetime=now)

        today_start_jalali = today_jalai.replace(hour=0, minute=0, second=0, microsecond=0)
        today_jalali = jdatetime.datetime.fromgregorian(datetime=now)

        month_start_jalali = today_start_jalali.replace(day=1)
        month_start = self.to_aware_gregorian(month_start_jalali)
        
        successful_orders = OrderModel.objects.filter(status=OrderStatusType.succes.value)

        
        context["total_sales"] = self.get_sales_sum(successful_orders)      
        context["month_sales"] = self.get_sales_sum(successful_orders, since=month_start)

        context["total_orders"] = OrderModel.objects.count()
        context["month_orders"] = OrderModel.objects.filter(created_date__gte=month_start)[:5]
        
        context['total_customers'] = User.objects.count()

        context['total_products'] = ProductModel.objects.count()
        
        # context["today_jalali_full"] = today_jalali.strftime("%Y/%m/%d")
        context["current_month_name"] = today_jalali.j_months_fa[today_jalali.month - 1]

        # cancelled=>faild pending complete delivered=>succes
        
        
        return context

    def to_aware_gregorian(self, jalali_dt):
        gregorian_dt = jalali_dt.togregorian()
        if timezone.is_naive(gregorian_dt):
            gregorian_dt = timezone.make_aware(gregorian_dt)
        return gregorian_dt

    def get_sales_sum(self, queryset, since=None):
        if since:
            queryset = queryset.filter(created_date__gte=since)
        result = queryset.aggregate(total=Sum("total_price"))
        return result["total"] or 0
    
    
class AdminSecurityEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, PasswordChangeView):
    template_name = 'dashboard/admin/settings/settings.html'
    form_class = AdminPasswordChangeForm
    success_url = reverse_lazy("dashboard:admin:security-edit")
    success_message = 'رمز با موفقیت عوض شد'
    
    
class AdminOrdersView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, ListView):
    template_name = 'dashboard/admin/orders/orders.html'
    context_object_name = 'orders'
    paginate_by = 5
    
    def get_queryset(self):
        queryset = OrderModel.objects.all()
        
        # if q := self.request.GET.get('q'):
        #     queryset = queryset.filter()

        order_status = self.request.GET.get('order-status')
        if order_status == 'complete':
            queryset = queryset.filter(status=OrderStatusType.complete.value)
        if order_status == 'pending':
            queryset = queryset.filter(status=OrderStatusType.pending.value)
        if order_status == 'succes':
            queryset = queryset.filter(status=OrderStatusType.succes.value)
        if order_status == 'faild':
            queryset = queryset.filter(status=OrderStatusType.faild.value)
        if order_status == 'all':
            pass

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        now = timezone.now()
        today_jalai = jdatetime.datetime.fromgregorian(datetime=now)

        today_start_jalali = today_jalai.replace(hour=0, minute=0, second=0, microsecond=0)

        month_start_jalali = today_start_jalali.replace(day=1)
        month_start = self.to_aware_gregorian(month_start_jalali)
        
        context["total_orders"] = OrderModel.objects.count()
        context["month_orders"] = OrderModel.objects.filter(created_date__gte=month_start)[:5]
        context['success_orders'] = OrderModel.objects.filter(status=OrderStatusType.succes.value).count()
        
        context['pending_orders'] = OrderModel.objects.filter(status=OrderStatusType.pending.value).count()
        context['complete_orders'] = OrderModel.objects.filter(status=OrderStatusType.complete.value).count()
        context['faild_orders'] = OrderModel.objects.filter(status=OrderStatusType.faild.value).count()

        return context

    def to_aware_gregorian(self, jalali_dt):    
        gregorian_dt = jalali_dt.togregorian()
        if timezone.is_naive(gregorian_dt):
            gregorian_dt = timezone.make_aware(gregorian_dt)
        return gregorian_dt

    def get_sales_sum(self, queryset, since=None):
        if since:
            queryset = queryset.filter(created_date__gte=since)
        result = queryset.aggregate(total=Sum("total_price"))
        return result["total"] or 0


class AdminOrdersDetailView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, DetailView):
    template_name = 'dashboard/admin/orders/orders-detail.html'
    queryset = OrderModel.objects.all()

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


class AdminProductDetailEditView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = 'dashboard/admin/products/edit-products.html'
    success_message = 'ویرایش فرم با موفقیت انجام شد'
    queryset = ProductModel.objects.all()
    form_class = AdminProductDetailEditFrom
    context_object_name = 'product'

    def get_success_url(self):
        return reverse_lazy('dashboard:admin:edit-products', kwargs={'pk': self.get_object().pk})


class AdminAddProductView(LoginRequiredMixin, HasAdminAccessPermission, SuccessMessageMixin, CreateView):
    template_name = "dashboard/admin/products/add-product.html"
    success_message = 'افزودن محصول با موفقیت انجام شد'
    queryset = ProductModel.objects.all()
    form_class = AdminProductDetailEditFrom
    context_object_name = 'product'
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('dashboard:admin:add-product')


class AdminProductsDeleteView(LoginRequiredMixin, HasAdminAccessPermission, DeleteView):
    success_url = reverse_lazy("dashboard:admin:products-list")
    queryset = ProductModel.objects.all()
    
    def form_valid(self, form):
        messages.success(self.request, 'محصول با موفقیت حذف شد')
        return super().form_valid(form)
    
    
class AdminCustomersView(TemplateView):
    template_name = 'dashboard/admin/customers/customers.html'

