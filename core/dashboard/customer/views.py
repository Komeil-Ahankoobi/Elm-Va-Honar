from django.views.generic import (
    TemplateView,
    ListView,
    UpdateView,
    CreateView,
    DeleteView,
    DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView


from ..permissions import HasCustomerAccessPermission
from order.models import (
    UserAddressModel,
    OrderModel
)
from .forms import (
    UserAddressForm,
    CustomerPasswordChangeForm
)
class CustomerDashboardHomeView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = 'dashboard/customer/main/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] =  User.objects.filter(username=self.request.user.username)
    
class CustomerDashboardAddressesView(LoginRequiredMixin, HasCustomerAccessPermission, ListView):
    template_name = 'dashboard/customer/addresses/address-list.html'
    context_object_name = 'addresses'
    
    def get_queryset(self):
        queryset = UserAddressModel.objects.filter(user=self.request.user) 
        return queryset


class CustomerDashboardCreateAddressView(LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, CreateView):
    template_name = 'dashboard/customer/addresses/address-create.html'
    form_class = UserAddressForm
    success_message = 'آدرس شما با موفقیت ایجاد شد'
    
    def get_queryset(self):
        return UserAddressModel.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        super().form_valid(form)
        return redirect(reverse_lazy('dashboard:customer:address-list'))

    def get_success_url(self):
        return reverse_lazy('dashboard:customer:address-list')
    

class CustomerDashboardEditAddressView(LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, UpdateView):
    template_name = 'dashboard/customer/addresses/address-edit.html'
    form_class = UserAddressForm
    success_message = 'آدرس شما با موفقیت ویرایش شد'
    context_object_name = 'address'


    def get_queryset(self):
        return UserAddressModel.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('dashboard:customer:address-list')


class CustomerDashboardDeleteAddressView(LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, DeleteView):
    template_name = 'dashboard/customer/addresses/address-delete.html'
    success_message = 'آدرس شما با موفقیت حذف شد'

    def get_queryset(self):
        return UserAddressModel.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('dashboard:customer:address-list')


class CustomerDashboardSettingView(LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, PasswordChangeView):
    template_name = 'dashboard/customer/settings/customer-setting.html'
    form_class = CustomerPasswordChangeForm
    success_url = reverse_lazy("dashboard:customer:setting")
    success_message = 'رمز با موفقیت عوض شد'


class CustomerDashboardOrderView(LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, ListView):
    template_name = 'dashboard/customer/orders/order-list.html'
    context_object_name = 'orders'
    paginate_by = 3
    
    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user)


class CustomerDashboardOrderDetailView(LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, DetailView):
    template_name = 'dashboard/customer/orders/order-detail.html'
    
    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user)