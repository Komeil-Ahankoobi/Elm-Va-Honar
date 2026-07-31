from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "website/home.html"

class AboutView(TemplateView):
    template_name = "website/about.html" 

class RuleQuView(TemplateView):
    template_name = 'website/rule_qu.html'