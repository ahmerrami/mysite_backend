# fournisseurs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... autres URLs
    path('get_beneficiaires/', views.get_beneficiaires, name='get_beneficiaires'),
    path('get_comptes_tresorerie/', views.get_comptes_tresorerie, name='get_comptes_tresorerie'),
    path('get-contrats/', views.get_contrats_all, name='get_contrats'),
    path('get-factures/', views.get_factures_all, name='get_factures'),
    path('update-facture-association/', views.update_facture_association, name='update_facture_association'),
    path('update-montant-ordre-virement/', views.update_montant_ordre_virement, name='update_montant_ordre_virement'),
    path('ordrevirement/generate-ov-pdf/<int:pk>/', views.generate_ov_pdf, name='generate_ov_pdf'),
]