from django.urls import path
from .views import CryptoList


urlpatterns = [
    path('', CryptoList.as_view(), name='crypto')
]
