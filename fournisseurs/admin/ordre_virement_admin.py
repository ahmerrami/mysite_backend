# admin.py
from django.contrib import admin
from django import forms
from django.conf import settings
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields

from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.html import format_html
from django.urls import reverse

from fournisseurs.filters import get_factures_queryset
from fournisseurs.models.beneficiaire_model import Beneficiaire
from fournisseurs.models.compte_tresorerie_model import CompteTresorerie
from fournisseurs.models.ordre_virement_model import OrdreVirement
from fournisseurs.models.facture_model import Facture
from fournisseurs.views import generate_ov_pdf

from fournisseurs.admin.facture_admin import fournisseur_admin

#@admin.register(Beneficiaire)

import csv

# Define a custom resource for OV
class OrdreVirementResource(resources.ModelResource):
    beneficiaire = fields.Field(attribute='beneficiaire__raison_sociale', column_name='Beneficiaire')
    compte_tresorerie = fields.Field(attribute='compte_tresorerie__rib', column_name='Compte_beneficiaire')
    compte_tresorerie_emetteur = fields.Field(attribute='compte_tresorerie_emetteur__rib', column_name='Compte_emetteur')

    class Meta:
        model = OrdreVirement
        fields = [
            "reference", "type_ov", "mode_execution", "beneficiaire", "compte_tresorerie", "compte_tresorerie_emetteur",
            "montant", "valide_pour_signature", "date_remise_banque", "OV_remis_banque_pdf",
            "remis_a_banque", "date_operation_banque", "avis_debit_pdf", "compte_debite"
        ]
        #fields = ('beneficiaire', 'contrat', 'moe', 'num_facture', 'date_facture', 'date_echeance', 'montant_ttc', 'mnt_RAS_IS', 'mnt_RAS_TVA', 'mnt_RG', 'mnt_net_apayer', 'ordre_virement','statut')
        export_order = ["beneficiaire", "montant", "compte_tresorerie", "compte_tresorerie_emetteur"]

class OrdreVirementForm(forms.ModelForm):
    ordre_virement_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    factures = forms.ModelMultipleChoiceField(
        queryset=Facture.objects.none(),  # Initialement aucun choix
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
            # Ajouter le champ mnt_net_apayer dans le rendu des factures
            self.fields['factures'].label_from_instance = lambda obj: (
                f"{obj.num_facture} - Montant : {obj.montant_ttc} - Mnt net à payer : {obj.mnt_net_apayer} - Échéance : {obj.date_echeance}"
            )

        # Récupère le nom de la société depuis les paramètres de configuration
        societe_name = getattr(settings, 'SOCIETE', None)
        if societe_name:
            try:
                # Cherche le bénéficiaire correspondant au nom de la société
                societe = Beneficiaire.objects.get(raison_sociale=societe_name)
                # Restreint les choix du champ 'compte_bancaire_emetteur' à ceux associés à la société
                self.fields['compte_tresorerie_emetteur'].queryset = CompteTresorerie.objects.filter(
                    beneficiaire=societe, actif=True
                )
            except Beneficiaire.DoesNotExist:
                # Aucun compte bancaire n'est disponible si la société n'est pas trouvée
                self.fields['compte_tresorerie_emetteur'].queryset = CompteTresorerie.objects.none()
        else:
            # Aucun compte bancaire n'est disponible si le nom de la société n'est pas défini
            self.fields['compte_tresorerie_emetteur'].queryset = CompteTresorerie.objects.none()

# ##############################################################################

def export_ov_as_csv(modeladmin, request, queryset):
    """
    Exporte les Ordres de Virement sélectionnés en CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ordres_virement.csv"'

    writer = csv.writer(response)
    writer.writerow(['beneficiaire', 'montant', 'date_paiement'])

    for ov in queryset:
        writer.writerow([ov.beneficiaire.raison_sociale, ov.montant, ov.date_paiement])

    return response

export_ov_as_csv.short_description = "Exporter les OV en CSV"

# Enregistrement du modèle OrdreVirement dans l'administration Django
# @admin.register(OrdreVirement)

@admin.register(OrdreVirement, site=fournisseur_admin)
class OrdreVirementAdmin(ImportExportModelAdmin):
    form = OrdreVirementForm
    resource_class = OrdreVirementResource
    #list_display = ("reference", "beneficiaire", "montant", "valide_pour_signature", "remis_a_banque", "compte_debite", "generate_pdf_link")
    list_filter = ('mode_execution', 'valide_pour_signature', 'remis_a_banque')
    readonly_fields = ('created_by','updated_by','montant')
    list_per_page = 15
    actions = ['generate_ov_pdf_action','export_ov_as_csv']

    class Media:
        js = ('admin/js/jquery.init.js', 'fournisseurs/js/compte_tresorerie_filter.js',
              'fournisseurs/js/beneficiaire_filter.js', 'fournisseurs/js/affect_factures.js')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if 'factures' in form.cleaned_data:
            factures = form.cleaned_data['factures']
            factures.update(ordre_virement=obj)

    def get_readonly_fields(self, request, obj=None):
        """
        Rendre certains champs en lecture seule après certaines étapes.
        """
        fields = list(super().get_readonly_fields(request, obj) or [])
        if obj:
            if obj.remis_a_banque:
                fields.extend(["date_remise_banque", "OV_remis_banque_pdf", "remis_a_banque"])
            if obj.compte_debite and not request.user.is_superuser:
                fields.extend(["date_operation_banque", "avis_debit_pdf", "compte_debite"])
        return fields

    def get_fields(self, request, obj=None):
        """
        Personnalise les champs affichés en fonction de l'état de l'Ordre de Virement.
        """
        fields = [
            "ordre_virement_id", "reference", "type_ov", "mode_execution", "beneficiaire", "compte_tresorerie", "compte_tresorerie_emetteur",
            "montant", "valide_pour_signature", "date_remise_banque", "OV_remis_banque_pdf",
            "remis_a_banque", "date_operation_banque", "avis_debit_pdf", "compte_debite","factures"
        ]

        if not obj:  # Si l'objet n'existe pas
            fields.remove("valide_pour_signature")
            fields.remove("date_remise_banque")
            fields.remove("OV_remis_banque_pdf")
            fields.remove("remis_a_banque")
            fields.remove("date_operation_banque")
            fields.remove("avis_debit_pdf")
            fields.remove("compte_debite")
            fields.remove("factures")

        else:  # Si l'objet existe, les champs sont affichés en fonction du
                # statut de l'OV
            if not obj.valide_pour_signature:
                # Avant remise à la signature : cacher certains champs
                fields.remove("date_remise_banque")
                fields.remove("OV_remis_banque_pdf")
                fields.remove("remis_a_banque")
                fields.remove("date_operation_banque")
                fields.remove("avis_debit_pdf")
                fields.remove("compte_debite")
            elif not obj.remis_a_banque:
                # Avant remise à la banque : cacher certains champs
                fields.remove("date_operation_banque")
                fields.remove("avis_debit_pdf")
                fields.remove("compte_debite")

        return fields

    def get_list_display(self, request):
        """Affiche dynamiquement les colonnes selon le statut"""
        fields = ["reference", "beneficiaire", "montant", "valide_pour_signature", "remis_a_banque", "compte_debite"]

        # Afficher le lien PDF seulement si l'ordre est validé
        if any(obj.valide_pour_signature and not obj.remis_a_banque for obj in self.model.objects.all()):
            fields.append("generate_pdf_link")

        return fields

    def generate_pdf_link(self, obj):
        url = reverse('admin:generate_pdf', args=[obj.id])  # Prefixe 'admin:'
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

    def has_import_permission(self, request):
        return request.user.is_superuser


admin.site.register(OrdreVirement, OrdreVirementAdmin)