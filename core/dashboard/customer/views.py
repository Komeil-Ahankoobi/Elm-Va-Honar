from django.views.generic import (
    TemplateView,
    ListView,
    UpdateView,
    CreateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from order.models import OrderStatusType
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView


from ..permissions import HasCustomerAccessPermission
from order.models import UserAddressModel, OrderModel, OrderItemsModel
from .forms import UserAddressForm, CustomerPasswordChangeForm


class CustomerDashboardHomeView(
    LoginRequiredMixin, HasCustomerAccessPermission, TemplateView
):
    template_name = "dashboard/customer/main/main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = User.objects.filter(username=self.request.user.username)


class CustomerDashboardAddressesView(
    LoginRequiredMixin, HasCustomerAccessPermission, ListView
):
    template_name = "dashboard/customer/addresses/address-list.html"
    context_object_name = "addresses"

    def get_queryset(self):
        queryset = UserAddressModel.objects.filter(user=self.request.user)
        return queryset


class CustomerDashboardCreateAddressView(
    LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, CreateView
):
    template_name = "dashboard/customer/addresses/address-create.html"
    form_class = UserAddressForm
    success_message = "آدرس شما با موفقیت ایجاد شد"

    def get_queryset(self):
        return UserAddressModel.objects.filter(user=self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        super().form_valid(form)
        return redirect(reverse_lazy("dashboard:customer:address-list"))

    def get_success_url(self):
        return reverse_lazy("dashboard:customer:address-list")


class CustomerDashboardEditAddressView(
    LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, UpdateView
):
    template_name = "dashboard/customer/addresses/address-edit.html"
    form_class = UserAddressForm
    success_message = "آدرس شما با موفقیت ویرایش شد"
    context_object_name = "address"

    def get_queryset(self):
        return UserAddressModel.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("dashboard:customer:address-list")


class CustomerDashboardDeleteAddressView(
    LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, DeleteView
):
    template_name = "dashboard/customer/addresses/address-delete.html"
    success_message = "آدرس شما با موفقیت حذف شد"

    def get_queryset(self):
        return UserAddressModel.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("dashboard:customer:address-list")


class CustomerDashboardOrderView(
    LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, ListView
):
    template_name = "dashboard/customer/orders/order-list.html"
    context_object_name = "orders"
    paginate_by = 3

    def get_queryset(self):
        
        OrderModel.expire_stale_pending(user=self.request.user)

        return OrderModel.objects.filter(user=self.request.user)


class CustomerDashboardOrderDetailView(
    LoginRequiredMixin, HasCustomerAccessPermission, SuccessMessageMixin, DetailView
):
    template_name = "dashboard/customer/orders/order-detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return OrderModel.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object
        context["total_post_price"] = order.get_post_price()
        context["total_basket_price"] = order.get_total_price()
        return context



class CustomerDashboardCancelOrderView(
    LoginRequiredMixin, HasCustomerAccessPermission, View
):

    def post(self, request, pk):

        order = get_object_or_404(OrderModel, pk=pk, user=request.user)

        allowed_statuses = [
            OrderStatusType.pending.value,
            OrderStatusType.paid.value,
            OrderStatusType.processing.value,
        ]

        if order.status not in allowed_statuses:
            return JsonResponse(
                {"success": False, "message": "این سفارش دیگر قابل لغو نیست."}
            )

        paid_order = order.status in [
            OrderStatusType.paid.value,
            OrderStatusType.processing.value,
        ]

        order.status = OrderStatusType.cancelled.value
        order.save(update_fields=["status", "updated_date"])

        if paid_order:
            message = (
                "سفارش شما لغو شد. \n"
                "برای پیگیری سفارش خود با شماره مغازه تماس بگیرید: "
                "33218734-026 - 9949819-0919"
            )
        else:
            message = "سفارش شما با موفقیت لغو شد."

        return JsonResponse({"success": True, "message": message})



class CustomerDashboardAjaxCreateAddressView(
    LoginRequiredMixin, HasCustomerAccessPermission, View
):
    def post(self, request):
        form = UserAddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": "آدرس شما با موفقیت ثبت شد",
                    "address": {
                        "id": address.id,
                        "address": address.address,
                        "state": address.state,
                        "city": address.city,
                        "zip_code": address.zip_code,
                    },
                }
            )

        return JsonResponse({"success": False, "errors": form.errors}, status=400)