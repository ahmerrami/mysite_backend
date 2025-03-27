# admin/contrat_admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from ..models.contrat_model import Contrat

#@admin.register(Contrat)
class ContratAdmin(ImportExportModelAdmin):
    list_display = ('numero_contrat', 'objet', 'beneficiaire')
    list_filter = ('moe','type_contrat')
    search_fields = ('numero_contrat',)
    readonly_fields = ('created_by','updated_by')
    list_per_page = 15

    def has_import_permission(self, request):
        return request.user.is_superuser

admin.site.register(Contrat, ContratAdmin)