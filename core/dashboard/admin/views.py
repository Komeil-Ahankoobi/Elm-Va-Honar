from django.views.generic import (
    TemplateView
)
from ..permissions import HasAdminAccessPermission

class AdminDashboardHomeView(HasAdminAccessPermission,TemplateView):
    template_name = 'dashboard/admin/main/main.html'


class AdminOrdersView(TemplateView):
    template_name = 'dashboard/admin/orders/orders.html'

class AdminOrdersDetailView(TemplateView):
    template_name = 'dashboard/admin/orders/orders-detail.html'

class AdminProductsView(TemplateView):
    template_name = 'dashboard/admin/products/products.html'

class AdminEditProductsView(TemplateView):
    template_name = 'dashboard/admin/products/edit-products.html'


class AdminCustomersView(TemplateView):
    template_name = 'dashboard/admin/customers/customers.html'


