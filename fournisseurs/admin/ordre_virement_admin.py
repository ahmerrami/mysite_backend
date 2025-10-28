# admin.py
from django.contrib import admin
from django import forms
from django.conf import settings
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from django.db.models.functions import Lower

############### Pour la génération de l'OV pdf
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from fournisseurs.views import generate_ov_pdf
###############

from fournisseurs.filters import get_factures_queryset
from fournisseurs.models.beneficiaire_model import Beneficiaire
from fournisseurs.models.compte_tresorerie_model import CompteTresorerie
from fournisseurs.models.ordre_virement_model import OrdreVirement
from fournisseurs.models.facture_model import Facture

from fournisseurs.admin.facture_admin import fournisseur_admin

import csv

class OrdreVirementResource(resources.ModelResource):
    beneficiaire = fields.Field(attribute='beneficiaire__raison_sociale', column_name='Beneficiaire')
    compte_tresorerie = fields.Field(attribute='compte_tresorerie__rib', column_name='Compte_beneficiaire')
    compte_tresorerie_emetteur = fields.Field(attribute='compte_tresorerie_emetteur__rib', column_name='Compte_emetteur')

    class Meta:
        model = OrdreVirement
        fields = [
            "reference", "type_ov", "mode_execution", "beneficiaire", "compte_tresorerie", "compte_tresorerie_emetteur",
            "montant", "valide_pour_signature", "date_remise_banque",
            "remis_a_banque", "date_operation_banque", "compte_debite"
        ]
        export_order = ["beneficiaire", "montant", "compte_tresorerie", "compte_tresorerie_emetteur"]

class OrdreVirementForm(forms.ModelForm):
    ordre_virement_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    factures = forms.ModelMultipleChoiceField(
        queryset=Facture.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Factures",
    )

    class Meta:
        model = OrdreVirement
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)

        if instance:
            self.fields['ordre_virement_id'].initial = instance.pk
            self.fields['factures'].queryset = get_factures_queryset(
                beneficiaire_id=instance.beneficiaire_id,
                ordre_virement_id=instance.pk
            )
            self.fields['factures'].label_from_instance = lambda obj: (
                f"{obj.num_facture} - Montant : {obj.montant_ttc} - Mnt net à payer : {obj.mnt_net_apayer} - Échéance : {obj.date_echeance}"
            )

        societe_name = getattr(settings, 'SOCIETE', None)
        if societe_name:
            try:
                societe = Beneficiaire.objects.get(raison_sociale=societe_name)
                self.fields['compte_tresorerie_emetteur'].queryset = CompteTresorerie.objects.filter(
                    beneficiaire=societe, actif=True
                )
            except Beneficiaire.DoesNotExist:
                self.fields['compte_tresorerie_emetteur'].queryset = CompteTresorerie.objects.none()
        else:
            self.fields['compte_tresorerie_emetteur'].queryset = CompteTresorerie.objects.none()

        # Configuration pour limiter aux bénéficiaires ayant des factures en attente
        beneficiaires_avec_factures_attente = Beneficiaire.objects.filter(
            actif=True,
            factures_beneficiaire__statut='attente'  # Factures en attente
        ).distinct().order_by(Lower('raison_sociale'))
        
        self.fields['beneficiaire'].queryset = beneficiaires_avec_factures_attente

def export_ov_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ordres_virement.csv"'

    writer = csv.writer(response)
    writer.writerow(['beneficiaire', 'montant', 'date_paiement'])

    for ov in queryset:
        writer.writerow([ov.beneficiaire.raison_sociale, ov.montant, ov.date_paiement])

    return response

export_ov_as_csv.short_description = "Exporter les OV en CSV"

@admin.register(OrdreVirement, site=fournisseur_admin)
class OrdreVirementAdmin(ImportExportModelAdmin):
    form = OrdreVirementForm
    resource_class = OrdreVirementResource
    list_filter = ('mode_execution', 'valide_pour_signature', 'remis_a_banque')
    readonly_fields = ('created_by','updated_by','montant')
    search_fields = ('beneficiaire__raison_sociale',)
    list_per_page = 15
    #actions = ['export_ov_as_csv']
    actions = ['generate_ov_pdf_action','export_ov_as_csv']

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'fournisseurs/js/compte_tresorerie_filter.js',
            'fournisseurs/js/beneficiaire_filter.js?v=4',  # Version mise à jour
            'fournisseurs/js/affect_factures.js'
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if 'factures' in form.cleaned_data:
            factures = form.cleaned_data['factures']
            factures.update(ordre_virement=obj)

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj) or [])
        if obj:
            if obj.remis_a_banque:
                fields.extend(["date_remise_banque", "remis_a_banque"])
            if obj.compte_debite and not request.user.is_superuser:
                fields.extend(["date_operation_banque", "compte_debite"])
        return fields

    def get_fields(self, request, obj=None):

        fields = [
            "ordre_virement_id", "reference", "type_ov", "mode_execution", "beneficiaire", "compte_tresorerie", "compte_tresorerie_emetteur",
            "montant", "valide_pour_signature", "date_remise_banque", "OV_remis_banque_pdf",
            "remis_a_banque", "date_operation_banque", "avis_debit_pdf", "compte_debite","factures"
        ]

        if not obj:
            for field in ["valide_pour_signature", "OV_remis_banque_pdf", "date_remise_banque", "remis_a_banque", "date_operation_banque", "avis_debit_pdf", "compte_debite", "factures"]:
                fields.remove(field)
        else:
            if not obj.valide_pour_signature:
                for field in ["date_remise_banque", "remis_a_banque", "date_operation_banque", "avis_debit_pdf", "compte_debite"]:
                    fields.remove(field)
            elif not obj.remis_a_banque:
                for field in ["date_operation_banque", "avis_debit_pdf", "compte_debite"]:
                    fields.remove(field)

        return fields

    def get_list_display(self, request):
        """Affiche dynamiquement les colonnes selon le statut"""
        fields = ["reference", "beneficiaire", "montant", "valide_pour_signature", "remis_a_banque", "compte_debite"]

        ############################### Afficher le lien PDF seulement si l'ordre est validé
        if any(obj.valide_pour_signature and not obj.remis_a_banque for obj in self.model.objects.all()):
            fields.append("generate_pdf_link")

        return fields

    ###########################
    # Dans la classe OrdreVirementAdmin
    def generate_pdf_link(self, obj):
        url = reverse('fournisseur_admin:generate_pdf', args=[obj.id])  # Prefixe 'admin:'
        if obj.valide_pour_signature and not obj.remis_a_banque:
            return format_html('<a href="{}" target="_blank">📄 Télécharger PDF</a>', url)
        return "Non disponible"

    generate_pdf_link.short_description = "Générer PDF"

    def generate_pdf_action(self, request, queryset):
        if queryset.count() == 1:
            obj = queryset.first()
            return HttpResponseRedirect(reverse('admin:generate_pdf', args=[obj.id]))  # Prefixe 'admin:'
        else:
            self.message_user(request, "Sélectionnez un seul ordre de virement.", level='error')

    generate_pdf_action.short_description = "Générer un PDF pour l'ordre sélectionné"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-pdf/<int:ordre_virement_id>/', self.admin_site.admin_view(self.generate_pdf_view), name='generate_pdf'),
        ]
        return custom_urls + urls

    def generate_pdf_view(self, request, ordre_virement_id):
        return generate_ov_pdf(request, ordre_virement_id)