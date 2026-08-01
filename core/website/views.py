from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect

from .forms import NewsLetterForm
from shop.models import ProductModel


class HomeView(TemplateView):
    template_name = "website/home.html"
    
    def post(self, request, *args, **kwargs):
        form = NewsLetterForm(request.POST)
        if form.is_valid():
            messages.success(request, 'شماره تلفن شما با موفقیت ثبت شد')
            form.save()
        else:
            messages.error(request, 'شماره تلفن وارد شده معتبر نمی باشد')
        return redirect('website:home')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['four_product'] = ProductModel.objects.all().order_by('-created_date')[:4]
        return context

class AboutView(TemplateView):
    template_name = "website/about.html" 

class RuleQuView(TemplateView):
    template_name = 'website/rule_qu.html'