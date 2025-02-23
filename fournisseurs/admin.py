# admin.py
from django.contrib import admin
from django import forms
from django.conf import settings
from import_export.admin import ImportExportModelAdmin

from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.html import format_html
from django.urls import reverse

from .filters import get_factures_queryset
from .models import Beneficiaire, CompteTresorerie, Contrat, OrdreVirement, Facture
from .views import generate_ov_pdf

@admin.register(Beneficiaire)
class BeneficiaireAdmin(ImportExportModelAdmin):
    list_display = ('raison_sociale', 'registre_commerce', 'identifiant_fiscale', 'code_ice')
    search_fields = ('raison_sociale', 'identifiant_fiscale')


@admin.register(CompteTresorerie)
class CompteTresorerieAdmin(ImportExportModelAdmin):
    list_display = ('beneficiaire', 'banque', 'rib')
    search_fields = ('beneficiaire__raison_sociale', 'banque', 'rib')
    list_filter = ('beneficiaire', 'banque')


#@admin.register(Contrat)
class ContratAdmin(ImportExportModelAdmin):
    list_display = ('numero_contrat', 'objet', 'beneficiaire')
    search_fields = ('numero_contrat',)

admin.site.register(Contrat, ContratAdmin)

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
                    beneficiaire=societe
                )
            except Beneficiaire.DoesNotExist:
                # Aucun compte bancaire n'est disponible si la société n'est pas trouvée
                self.fields['compte_tresorerie_emetteur'].queryset = CompteTresorerie.objects.none()
        else:
            # Aucun compte bancaire n'est disponible si le nom de la société n'est pas défini
            self.fields['compte_tresorerie_emetteur'].queryset = CompteTresorerie.objects.none()

# Enregistrement du modèle OrdreVirement dans l'administration Django
# @admin.register(OrdreVirement)

class OrdreVirementAdmin(ImportExportModelAdmin):
    form = OrdreVirementForm
    list_display = ('beneficiaire', 'montant', 'date_ov', 'valide_pour_signature', 'remis_a_banque', 'generate_pdf_link')
    list_filter = ('valide_pour_signature', 'remis_a_banque')
    readonly_fields = ['montant']
    actions = ['generate_ov_pdf_action']

    class Media:
        js = ('admin/js/jquery.init.js', 'fournisseurs/js/compte_tresorerie_filter.js',
              'fournisseurs/js/beneficiaire_filter.js', 'fournisseurs/js/affect_factures.js')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if 'factures' in form.cleaned_data:
            factures = form.cleaned_data['factures']
            factures.update(ordre_virement=obj)

    def generate_pdf_link(self, obj):
        url = reverse('admin:generate_pdf', args=[obj.id])  # Prefixe 'admin:'
        return format_html('<a href="{}" target="_blank">📄 Télécharger PDF</a>', url)

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

admin.site.register(OrdreVirement, OrdreVirementAdmin)

@admin.register(Facture)
class FactureAdmin(ImportExportModelAdmin):
    list_display = ('num_facture', 'beneficiaire', 'montant_ttc', 'mnt_net_apayer', 'date_echeance', 'ordre_virement','statut')
    search_fields = ('num_facture', 'beneficiaire__raison_sociale')
    list_filter = ('statut','date_echeance', 'beneficiaire')
    readonly_fields = ('ordre_virement','statut',)

    class Media:
        js = ('admin/js/jquery.init.js', 'fournisseurs/js/contrat_filter.js')