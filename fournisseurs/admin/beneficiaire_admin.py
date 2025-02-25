# admin/beneficiaire.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from ..models.beneficiaire_model import Beneficiaire

@admin.register(Beneficiaire)
class BeneficiaireAdmin(ImportExportModelAdmin):
    list_display = ('raison_sociale', 'registre_commerce', 'identifiant_fiscale', 'code_ice')
    search_fields = ('raison_sociale', 'identifiant_fiscale')