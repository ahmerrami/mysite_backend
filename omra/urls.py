# urls.py
from django.urls import path
from .views import OmraListAPIView

urlpatterns = [
    path('images/', OmraListAPIView.as_view(), name='omra-liste'),
]