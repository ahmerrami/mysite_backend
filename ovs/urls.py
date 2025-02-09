# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... autres URLs
    path('get_beneficiaires/', views.get_beneficiaires, name='get_beneficiaires'),
    path('get_comptes_bancaires/', views.get_comptes_bancaires, name='get_comptes_bancaires'),
    path('get-factures/', views.get_factures_all, name='get_factures'),
]