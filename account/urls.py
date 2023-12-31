from django.urls import path, include
from .views import (
    UserRegisterView,
    LoginAPIView,
    PasswordTokenCheckAPI,
    PasswordResetEmail,
    SetNewPasswordAPIView,
    LogoutAPIView,
    VerifyEmailCode
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    # path('verify-email/', VerifyEmail.as_view(), name='verify-email'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('password-reset-email/', PasswordResetEmail.as_view(), name='password-reset-email'),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyEmailCode.as_view(), name='verify-email')
]
