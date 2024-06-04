# urls.py
from django.urls import path
from .views import VilleListAPIView, PeriodeListAPIView, StageCreateAPIView

urlpatterns = [
    path('form-stage/create/', StageCreateAPIView.as_view(), name='form-stage-create'),
    path('villes/', VilleListAPIView.as_view(), name='villes-liste'),
    path('periodes/', PeriodeListAPIView.as_view(), name='periodes-liste'),
]