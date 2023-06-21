from django.urls import path, include
from .views import UserRegisterView, VerifyEmail, LoginAPIView
from rest_framework import urls

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmail.as_view(), name='verify-email'),
    path('login/', LoginAPIView.as_view(), name='login'),
]