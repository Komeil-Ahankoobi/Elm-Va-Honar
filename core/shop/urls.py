from django.urls import path, re_path

from . import views

app_name = 'shop'

urlpatterns = [
    path("", views.ShopProductView.as_view(), name="show-product-view"),
    re_path(r"product/(?P<slug>[-\w]+)/detail/",views.ShopProductDetailView.as_view(),name="show-product-detail-view"),
]