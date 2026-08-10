from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/verify/', views.VerifyRegisterView.as_view(), name='verify_register'),

    path('login/', views.LoginView.as_view(), name='login'),
    path('login/verify/', views.VerifyLoginView.as_view(), name='verify_login'),

    path('logout/', views.LogoutView.as_view(), name='logout'),
]