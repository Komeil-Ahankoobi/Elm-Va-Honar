from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('session/add-product/', views.SessionAddProduct.as_view(), name='session-add-product'),
    path('session/cart/summary/', views.SessionCartSummary.as_view(), name='session-cart-summary'),
    path('session/update-quantity/', views.UpdateCartQuantity.as_view(), name='update-quantity'),
    path('session/delete-product/', views.DeleteProduct.as_view(), name='delete-product'),
]