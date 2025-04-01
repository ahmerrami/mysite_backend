from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from import_export import resources, fields
from import_export.admin import ExportMixin
from import_export.formats import base_formats
from django.utils import timezone
from fournisseurs.models.facture_model import Facture, Avoir


class FactureResourceSTD(resources.ModelResource):
    beneficiaire = fields.Field(attribute='beneficiaire__raison_sociale', column_name='Beneficiaire')
    contrat = fields.Field(attribute='contrat__numero_contrat', column_name='Contrat')
    moe = fields.Field(attribute='contrat__moe', column_name='MOE')

    class Meta:
        model = Facture
        fields = ('beneficiaire', 'contrat', 'moe', 'num_facture', 'date_facture',
                 'date_echeance', 'montant_ttc', 'mnt_RAS_IS', 'mnt_RAS_TVA',
                 'mnt_RG', 'mnt_net_apayer', 'ordre_virement', 'statut')
        export_order = fields


class FactureResourceDLP(resources.ModelResource):
    beneficiaire = fields.Field(attribute='beneficiaire__raison_sociale', column_name='Fournisseur')
    contrat = fields.Field(attribute='contrat__numero_contrat', column_name='Contrat')
    moe = fields.Field(attribute='contrat__moe', column_name='MOE')
    ice = fields.Field(attribute='beneficiaire__code_ice', column_name='ICE')
    rc = fields.Field(attribute='beneficiaire__registre_commerce', column_name='RC')
    echeance_contractuelle = fields.Field(attribute='contrat__mode_paiement', column_name='Echeance contractuelle')
    date_reglement = fields.Field(attribute='ordre_virement__date_remise_banque', column_name='Date règlement')

    class Meta:
        model = Facture
        fields = ('moe', 'contrat', 'date_facture', 'num_facture', 'montant_ht',
                 'montant_ttc', 'beneficiaire', 'ice', 'rc', 'date_execution',
                 'echeance_contractuelle', 'date_reglement', 'mnt_net_apayer')
        export_order = fields


@admin.register(Facture)
class FactureAdmin(ExportMixin, admin.ModelAdmin):
    change_list_template = "admin/fournisseurs/facture/change_list.html"
    
    fields = ('beneficiaire', 'contrat', 'num_facture', 'date_facture',
             'date_echeance', 'montant_ht', 'mnt_tva', 'montant_ttc',
             'mnt_RAS_IS', 'mnt_RAS_TVA', 'mnt_RG', 'mnt_net_apayer',
             'proforma_pdf', 'facture_pdf', 'PV_reception_pdf', 'date_execution',
             'ordre_virement', 'statut')
    
    list_display = ('num_facture', 'beneficiaire', 'montant_ttc',
                   'mnt_net_apayer', 'date_echeance', 'ordre_virement')
    
    search_fields = ('num_facture', 'beneficiaire__raison_sociale')
    list_filter = ('statut', 'date_echeance', 'beneficiaire')
    readonly_fields = ('montant_ttc', 'mnt_net_apayer', 'created_by',
                      'updated_by', 'ordre_virement', 'date_paiement', 'statut')
    list_per_page = 25
    list_select_related = ('beneficiaire', 'contrat', 'ordre_virement')
    actions = ["export_std_selected", "export_dlp_selected"]

    class Media:
        js = ('admin/js/jquery.init.js', 'fournisseurs/js/contrat_filter.js')

    def export_std_selected(self, request, queryset):
        return self.process_export(request, FactureResourceSTD(), queryset)
    
    export_std_selected.short_description = _("Exporter la sélection (Standard)")
    
    def export_dlp_selected(self, request, queryset):
        return self.process_export(request, FactureResourceDLP(), queryset)
    
    export_dlp_selected.short_description = _("Exporter la sélection (Délais Paiement)")
    
    def process_export(self, request, resource, queryset=None):
        if queryset is None:
            queryset = self.get_queryset(request)
        
        dataset = resource.export(queryset)
        export_format = request.POST.get('format', 'csv')
        
        if export_format == 'xlsx':
            export_data = dataset.xlsx
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_extension = 'xlsx'
        else:
            export_data = dataset.csv
            content_type = 'text/csv'
            file_extension = 'csv'
        
        export_type = 'dlp' if isinstance(resource, FactureResourceDLP) else 'std'
        response = HttpResponse(export_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="export_{export_type}_{timezone.now().date()}.{file_extension}"'
        return response


@admin.register(Avoir)
class AvoirAdmin(admin.ModelAdmin):
    fields = ('num_facture', 'facture_associee', 'date_facture', 'date_echeance',
              'montant_ht', 'mnt_tva', 'montant_ttc', 'mnt_RAS_TVA', 'mnt_RAS_IS',
              'mnt_RG', 'mnt_net_apayer')
    readonly_fields = ('date_echeance', 'montant_ttc', 'mnt_net_apayer')
    list_display = ('num_facture', 'facture_associee', 'montant_ttc', 'date_facture')
    list_select_related = ('facture_associee',)

    def has_import_permission(self, request):
        return request.user.is_superuser