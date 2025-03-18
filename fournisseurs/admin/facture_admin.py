# facture_admin.py
from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from ..models.facture_model import Facture

# Define a custom resource for Facture
class FactureResource(resources.ModelResource):
    beneficiaire = fields.Field(attribute='beneficiaire__raison_sociale', column_name='Beneficiaire')
    contrat = fields.Field(attribute='contrat__numero_contrat', column_name='Contrat')

    class Meta:
        model = Facture
        fields = ('beneficiaire', 'contrat', 'num_facture', 'date_facture', 'date_echeance', 'montant_ttc', 'mnt_RAS_IS', 'mnt_RAS_TVA', 'mnt_RG', 'mnt_net_apayer', 'ordre_virement','statut')
        export_order = fields

class FactureAdmin(ImportExportModelAdmin):
    resource_class = FactureResource
    list_display = ('num_facture', 'beneficiaire', 'montant_ttc', 'mnt_net_apayer', 'date_echeance', 'ordre_virement','statut')
    search_fields = ('num_facture', 'beneficiaire__raison_sociale')
    list_filter = ('statut','date_echeance', 'beneficiaire')
    readonly_fields = ('created_by','updated_by','ordre_virement','date_paiement','statut',)

    class Media:
        js = ('admin/js/jquery.init.js', 'fournisseurs/js/contrat_filter.js')

admin.site.register(Facture, FactureAdmin)