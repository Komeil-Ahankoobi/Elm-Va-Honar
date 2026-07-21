from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect

class DashboardHomeView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff and not request.user.is_superuser:
                return redirect(reverse_lazy('dashboard:admin:home'))
            if not request.user.is_staff and not request.user.is_superuser:
                return redirect(reverse_lazy('dashboard:customer:home'))
        else:
            return redirect(reverse_lazy("accounts:login"))
        return super().dispatch(request, *args, **kwargs)