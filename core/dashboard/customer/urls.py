from django.urls import path, include

from . import views

app_name = 'customer'

urlpatterns = [
    path("home/", views.CustomerDashboardHomeView.as_view(), name="home"),

    path("addresses/list", views.CustomerDashboardAddressesView.as_view(), name="address-list"),
    path("addresses/create", views.CustomerDashboardCreateAddressView.as_view(), name="address-create"),
    path("addresses/<int:pk>/edit/", views.CustomerDashboardEditAddressView.as_view(), name="address-edit"),
    path("addresses/<int:pk>/delete/", views.CustomerDashboardDeleteAddressView.as_view(), name="address-delete"),

    path("setting/", views.CustomerDashboardSettingView.as_view(), name="setting"),

    path("order/", views.CustomerDashboardOrderView.as_view(), name="order"),
    path("order/<int:pk>/detail/", views.CustomerDashboardOrderDetailView.as_view(), name="order-detail"),
] 