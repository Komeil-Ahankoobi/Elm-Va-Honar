from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('checkout/', views.OrderCheckoutView.as_view(), name='order-checkout'),
    path('success/', views.OrderSuccessView.as_view(), name='order-success'),
    path('failed/', views.OrderFailedView.as_view(), name='order-failed'),
    path("validate-copon/",views.ValidateCoponView.as_view(),name="validate-copon"), 
]