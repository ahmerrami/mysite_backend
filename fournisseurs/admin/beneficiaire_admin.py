# admin/beneficiaire.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from ..models.beneficiaire_model import Beneficiaire

@admin.register(Beneficiaire)
class BeneficiaireAdmin(ImportExportModelAdmin):
    list_display = ('raison_sociale', 'registre_commerce', 'identifiant_fiscale', 'code_ice')
    search_fields = ('raison_sociale', 'identifiant_fiscale')
    readonly_fields = ('created_by','updated_by')
    list_per_page = 15

    def has_import_permission(self, request):
        return request.user.is_superuser
