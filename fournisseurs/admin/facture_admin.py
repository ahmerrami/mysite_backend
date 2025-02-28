# facture_admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from ..models.facture_model import Facture

@admin.register(Facture)
class FactureAdmin(ImportExportModelAdmin):
    list_display = ('num_facture', 'beneficiaire', 'montant_ttc', 'mnt_net_apayer', 'date_echeance', 'ordre_virement','statut')
    search_fields = ('num_facture', 'beneficiaire__raison_sociale')
    list_filter = ('statut','date_echeance', 'beneficiaire')
    readonly_fields = ('created_by','updated_by','ordre_virement','date_paiement','statut',)

    class Media:
        js = ('admin/js/jquery.init.js', 'fournisseurs/js/contrat_filter.js')