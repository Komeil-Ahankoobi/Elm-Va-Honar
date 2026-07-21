from django.views.generic import (
    TemplateView
)

from ..permissions import HasCustomerAccessPermission

class CustomerDashboardHomeView(HasCustomerAccessPermission, TemplateView):
    template_name = 'dashboard/customer/customer.html'
