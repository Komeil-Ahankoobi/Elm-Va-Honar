from django.urls import path, include

from . import views

app_name = 'admin'

urlpatterns = [
    path("home/", views.AdminDashboardHomeView.as_view(), name="home"),
    path("orders/", views.AdminOrdersView.as_view(), name="orders"),
    path("orders/details", views.AdminOrdersDetailView.as_view(), name="orders-detail"),
    path("products/", views.AdminProductsView.as_view(), name="products"),
    path("products/edit/", views.AdminEditProductsView.as_view(), name="edit-products"),
    path("customers/", views.AdminCustomersView.as_view(), name="customers"),


]