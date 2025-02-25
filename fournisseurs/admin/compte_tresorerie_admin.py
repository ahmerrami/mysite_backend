# admin/compte_tresorerie_admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from ..models.compte_tresorerie_model import CompteTresorerie

@admin.register(CompteTresorerie)
class CompteTresorerieAdmin(ImportExportModelAdmin):
    list_display = ('beneficiaire', 'banque', 'rib')
    search_fields = ('beneficiaire__raison_sociale', 'banque', 'rib')
    list_filter = ('beneficiaire', 'banque')
