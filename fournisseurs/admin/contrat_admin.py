# admin/contrat_admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from ..models.contrat_model import Contrat

#@admin.register(Contrat)
from fournisseurs.admin.facture_admin import fournisseur_admin

#@admin.register(Beneficiaire)
@admin.register(Contrat, site=fournisseur_admin)
class ContratAdmin(ImportExportModelAdmin):
    list_display = ('numero_contrat', 'objet', 'beneficiaire')
    list_filter = ('moe','type_contrat')
    search_fields = ('numero_contrat','beneficiaire__raison_sociale',)
    #search_fields = ('contrat__numero_contrat', 'num_facture', 'beneficiaire__raison_sociale')
    readonly_fields = ('created_by','updated_by')
    list_per_page = 15

    def has_import_permission(self, request):
        return request.user.is_superuser

#admin.site.register(Contrat, ContratAdmin)