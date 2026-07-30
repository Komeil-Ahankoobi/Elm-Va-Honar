from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from .forms import (
    UserRegisterForm, 
    UserLoginForm
)


# Create your views here.
class LoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    form_class = UserLoginForm

class RegisterView(SuccessMessageMixin, CreateView):
    template_name = 'accounts/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('accounts:login')
    success_message = 'ثبت نام شما با موفقیت انجام شد'

    def form_valid(self, form):
        response = super().form_valid(form)  
        profile = self.object.user_profile
        profile.first_name = form.cleaned_data['first_name']
        profile.last_name = form.cleaned_data['last_name']
        profile.phone_number = form.cleaned_data['phone_number']
        profile.save()
        return response