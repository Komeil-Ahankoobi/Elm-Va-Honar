from django.urls import path
from .views import PaymentRequestView, PaymentVerifyView

app_name = "payment"

urlpatterns = [
    path("request/<int:order_id>/", PaymentRequestView.as_view(), name="request"),
    path("verify/", PaymentVerifyView.as_view(), name="verify"),
]