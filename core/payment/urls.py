from django.urls import path

from .views import ParsianVerifyView, PaymentRequestView, PaymentVerifyView

app_name = "payment"

urlpatterns = [
    path("request/<int:order_id>/", PaymentRequestView.as_view(), name="request"),
    # callback زرین‌پال (بدون تغییر)
    path("verify/", PaymentVerifyView.as_view(), name="verify"),
    # callback پارسیان
    path("verify/parsian/", ParsianVerifyView.as_view(), name="verify-parsian"),
]
