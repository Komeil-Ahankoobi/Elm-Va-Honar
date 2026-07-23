from django.urls import path, include

from . import views

app_name = 'admin'

urlpatterns = [
    path("home/", views.AdminDashboardHomeView.as_view(), name="home"),
    
    path("security-edit/", views.AdminSecurityEditView.as_view(), name="security-edit"),
    
    path("orders/", views.AdminOrdersView.as_view(), name="orders"),
    path("orders/details", views.AdminOrdersDetailView.as_view(), name="orders-detail"),
    
    path('products/list', views.AdminProductsListView.as_view(), name='products-list'), 
    path("products/<int:pk>/detail/edit/", views.AdminProductDetailEditView.as_view(), name="edit-products"),
    path("products/add-product/", views.AdminAddProductView.as_view(), name="add-product"),
    path('products/<int:pk>/delete', views.AdminProductsDeleteView.as_view(), name='product-delete'), 
    
    path("customers/", views.AdminCustomersView.as_view(), name="customers"),
]