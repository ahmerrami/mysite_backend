# admin/contrat_admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from ..models.contrat_model import Contrat

#@admin.register(Contrat)
class ContratAdmin(ImportExportModelAdmin):
    list_display = ('numero_contrat', 'objet', 'beneficiaire')
    search_fields = ('numero_contrat',)

admin.site.register(Contrat, ContratAdmin)