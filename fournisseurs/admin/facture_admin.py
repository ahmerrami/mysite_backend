# facture_admin.py
from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from fournisseurs.models.facture_model import Facture, Avoir

# Define a custom resource for Facture
class FactureResource(resources.ModelResource):
    beneficiaire = fields.Field(attribute='beneficiaire__raison_sociale', column_name='Beneficiaire')
    contrat = fields.Field(attribute='contrat__numero_contrat', column_name='Contrat')
    moe = fields.Field(attribute='contrat__moe', column_name='moe')

    class Meta:
        model = Facture
        fields = ('beneficiaire', 'contrat', 'moe', 'num_facture', 'date_facture', 'date_echeance', 'montant_ttc', 'mnt_RAS_IS', 'mnt_RAS_TVA', 'mnt_RG', 'mnt_net_apayer', 'ordre_virement', 'statut')
        export_order = fields

class FactureAdmin(ImportExportModelAdmin):
    resource_class = FactureResource
    fields = ('beneficiaire', 'contrat', 'num_facture', 'date_facture', 'date_echeance', 'montant_ht', 'mnt_tva', 'montant_ttc', 'mnt_RAS_IS', 'mnt_RAS_TVA', 'mnt_RG', 'mnt_net_apayer', 'proforma_pdf', 'facture_pdf','PV_reception_pdf', 'date_execution','ordre_virement','statut')
    list_display = ('num_facture', 'beneficiaire', 'montant_ttc', 'mnt_net_apayer', 'date_echeance', 'ordre_virement','statut')
    search_fields = ('num_facture', 'beneficiaire__raison_sociale')
    list_filter = ('statut','date_echeance', 'beneficiaire')
    readonly_fields = ('montant_ttc', 'mnt_net_apayer', 'created_by','updated_by','ordre_virement','date_paiement','statut',)
    list_per_page = 15

    class Media:
        js = ('admin/js/jquery.init.js', 'fournisseurs/js/contrat_filter.js')

    def get_import_form(self): # Empêcher l'import
        return None

    def has_import_permission(self, request):
        return request.user.is_superuser

admin.site.register(Facture, FactureAdmin)

@admin.register(Avoir)
class AvoirAdmin(ImportExportModelAdmin):
    fields = ('num_facture', 'facture_associee', 'date_facture', 'date_echeance',
              'montant_ht', 'mnt_tva', 'montant_ttc', 'mnt_RAS_TVA', 'mnt_RAS_IS',
              'mnt_RG', 'mnt_net_apayer')

    readonly_fields = ('date_echeance', 'montant_ttc', 'mnt_net_apayer')

    def has_import_permission(self, request):
        return request.user.is_superuser