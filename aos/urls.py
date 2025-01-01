# urls.py
from django.urls import path
from .views import AOListAPIView

urlpatterns = [
    path('aos/', AOListAPIView.as_view(), name='aos-liste'),
]