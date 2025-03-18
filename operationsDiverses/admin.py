from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from .models import Compte, OperationDiverse, EcritureOperation
from .views import generate_operation_pdf

admin.site.register(Compte)

class EcritureOperationInline(admin.TabularInline):
    model = EcritureOperation
    extra = 2  # On oblige à avoir au moins deux écritures

    def has_add_permission(self, request, obj=None):
        """Empêcher l'ajout de nouvelles écritures si l'opération est valide."""
        if obj and obj.valide:
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Empêcher la suppression d'écritures si l'opération est valide."""
        if obj and obj.valide:
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """Empêcher la modification des écritures si l'opération est valide."""
        if obj and obj.valide:
            return False
        return super().has_change_permission(request, obj)

class OperationDiverseAdmin(admin.ModelAdmin):
    inlines = [EcritureOperationInline]
    list_display = ('libelle', 'date_operation', 'annee_comptable', 'valide', 'pdf_link')
    actions = ['generate_pdf_action']

    def has_delete_permission(self, request, obj=None):
        """Empêcher la suppression d'une opération si elle est valide."""
        if obj and obj.valide:
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        """Empêcher la modification d'une opération si elle est valide."""
        if obj and obj.valide:
            return False
        return super().has_change_permission(request, obj)

    def pdf_link(self, obj):
        if obj.valide:  # Vérifie si un fichier PDF est présent
            url = reverse('admin:operation_pdf', args=[obj.id])
            return format_html('<a href="{}" target="_blank">📄 Télécharger PDF</a>', url)
        return "Opération non encore équilibrée"

    pdf_link.short_description = "Générer PDF"


    def generate_pdf_action(self, request, queryset):
        if queryset.count() == 1:
            obj = queryset.first()
            return HttpResponseRedirect(reverse('admin:operation_pdf', args=[obj.id]))
        else:
            self.message_user(request, "Sélectionnez une seule opération pour générer un PDF.", level='error')

    generate_pdf_action.short_description = "Générer le PDF pour l'opération sélectionnée"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:operation_id>/pdf/', self.admin_site.admin_view(self.generate_pdf_view), name='operation_pdf'),
        ]
        return custom_urls + urls

    def generate_pdf_view(self, request, operation_id):
        return generate_operation_pdf(request, operation_id)

admin.site.register(OperationDiverse, OperationDiverseAdmin)
admin.site.register(EcritureOperation)
