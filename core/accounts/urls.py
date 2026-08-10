from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views


app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='website:home'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    path('password-reset/', 
         views.UserPasswordResetView.as_view(), 
         name='password_reset'),
    path('password-reset/done/', 
         views.UserPasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         views.UserPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         views.UserPasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
]