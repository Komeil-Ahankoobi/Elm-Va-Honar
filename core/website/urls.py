from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),    
    path("rule_qu/", views.RuleQuView.as_view(), name="rule_qu"),    
]