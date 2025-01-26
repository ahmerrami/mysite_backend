from django.contrib import admin
from django import forms
from django.conf import settings
from import_export.admin import ImportExportModelAdmin
from .models import Beneficiaire, CompteBancaire, Contrat, OrdreVirement, Facture


@admin.register(Beneficiaire)
class BeneficiaireAdmin(ImportExportModelAdmin):
    list_display = ('raison_sociale', 'registre_commerce', 'identifiant_fiscale', 'code_ice')
    search_fields = ('raison_sociale', 'identifiant_fiscale')


@admin.register(CompteBancaire)
class CompteBancaireAdmin(ImportExportModelAdmin):
    list_display = ('beneficiaire', 'banque', 'rib')
    search_fields = ('beneficiaire__raison_sociale', 'banque', 'rib')
    list_filter = ('beneficiaire', 'banque')


@admin.register(Contrat)
class ContratAdmin(ImportExportModelAdmin):
    list_display = ('numero_contrat', 'objet', 'beneficiaire')
    search_fields = ('numero_contrat',)


# Formulaire pour le modèle OrdreVirement
class OrdreVirementForm(forms.ModelForm):
    # Champ pour sélectionner plusieurs factures non affectées via des cases à cocher
    factures = forms.ModelMultipleChoiceField(
        queryset=Facture.objects.none(),  # Initialement aucun choix n'est disponible
        widget=forms.CheckboxSelectMultiple,  # Affiche les choix sous forme de cases à cocher
        required=False,  # Ce champ n'est pas obligatoire
        label="Factures non affectées",  # Intitulé affiché dans le formulaire
    )

    class Meta:
        # Associe ce formulaire au modèle OrdreVirement
        model = OrdreVirement
        # Inclut tous les champs du modèle dans le formulaire
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        # Récupère l'instance existante, si elle est passée en paramètre
        instance = kwargs.get('instance', None)
        # Appelle le constructeur de la classe parente
        super().__init__(*args, **kwargs)

        # Initialise le champ 'beneficiaire' si l'instance est définie
        if 'beneficiaire' in self.fields and instance:
            self.fields['beneficiaire'].initial = instance.beneficiaire

        # Restreint les choix du champ 'compte_bancaire' en fonction du bénéficiaire
        if 'compte_bancaire' in self.fields and instance and instance.beneficiaire:
            self.fields['compte_bancaire'].queryset = CompteBancaire.objects.filter(
                beneficiaire=instance.beneficiaire  # Filtre par le bénéficiaire associé
            )
            # Initialise le champ avec la valeur de l'instance actuelle
            self.fields['compte_bancaire'].initial = instance.compte_bancaire

        # Restreint les choix du champ 'factures' en fonction du bénéficiaire
        if instance and instance.beneficiaire:
            self.fields['factures'].queryset = Facture.objects.filter(
                beneficiaire=instance.beneficiaire,  # Filtre par bénéficiaire
                ordre_virement__isnull=True  # Exclut les factures déjà affectées à un ordre de virement
            )
        else:
            # Aucune facture n'est disponible si aucune instance ou bénéficiaire n'est spécifié
            self.fields['factures'].queryset = Facture.objects.none()

        # Récupère le nom de la société depuis les paramètres de configuration
        societe_name = getattr(settings, 'SOCIETE', None)
        if societe_name:
            try:
                # Cherche le bénéficiaire correspondant au nom de la société
                societe = Beneficiaire.objects.get(raison_sociale=societe_name)
                # Restreint les choix du champ 'compte_bancaire_emetteur' à ceux associés à la société
                self.fields['compte_bancaire_emetteur'].queryset = CompteBancaire.objects.filter(
                    beneficiaire=societe
                )
            except Beneficiaire.DoesNotExist:
                # Aucun compte bancaire n'est disponible si la société n'est pas trouvée
                self.fields['compte_bancaire_emetteur'].queryset = CompteBancaire.objects.none()
        else:
            # Aucun compte bancaire n'est disponible si le nom de la société n'est pas défini
            self.fields['compte_bancaire_emetteur'].queryset = CompteBancaire.objects.none()


# Enregistrement du modèle OrdreVirement dans l'administration Django
@admin.register(OrdreVirement)

class OrdreVirementAdmin(ImportExportModelAdmin):
    form = OrdreVirementForm
    list_display = ('beneficiaire', 'montant', 'date_ov', 'valide_pour_signature', 'valide_pour_paiement')
    list_filter = ('valide_pour_signature', 'valide_pour_paiement')

    class Media:
        js = ('admin/js/jquery.init.js', 'ovs/js/compte_bancaire_filter.js',
              'ovs/js/beneficiaire_filter.js', 'ovs/js/dynamic_factures.js')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if 'factures' in form.cleaned_data:
            factures = form.cleaned_data['factures']
            factures.update(ordre_virement=obj)


@admin.register(Facture)
class FactureAdmin(ImportExportModelAdmin):
    list_display = ('num_facture', 'beneficiaire', 'montant_ttc', 'date_echeance', 'ordre_virement')
    search_fields = ('num_facture', 'beneficiaire__raison_sociale')
    list_filter = ('date_echeance', 'beneficiaire')