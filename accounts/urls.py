# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('password/reset/', views.password_reset_request, name='password_reset'),
    path('password/reset/sent/', views.password_reset_sent, name='password_reset_sent'),
    path('password/reset/confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password/reset/complete/', views.password_reset_complete, name='password_reset_complete'),
]