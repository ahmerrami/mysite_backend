# /fournisseurs/admin/facture_admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import path, reverse
from django.shortcuts import render
from django import forms

from django.utils.timezone import now
from datetime import timedelta, datetime,date
from dateutil.relativedelta import relativedelta

from import_export import resources, fields
from import_export.admin import ExportMixin

from fournisseurs.models.facture_model import Facture, Avoir, Beneficiaire
from fournisseurs.filters import DateRangeFilter
from .dashboard import tableau_bord_view  # Importez la vue depuis le nouveau fichier

class FournisseurAdminSite(AdminSite):
    site_header = "Administration des Fournisseurs"
    site_title = "Fournisseurs Admin"
    index_title = "Tableau de bord"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('tableau-bord-fournisseurs/',
                self.admin_view(tableau_bord_view),
                name='tableau_bord_fournisseurs'),
            path('', self.admin_view(self.index)),
        ]
        return custom_urls + urls

    def index(self, request):
        return tableau_bord_view(request, self)

# ... (le reste de votre code existant)


fournisseur_admin = FournisseurAdminSite(name='fournisseur_admin')

# Cette classe est pour créer un lien dans l'admin principal
class FournisseursAdminLink(admin.ModelAdmin):
    def get_urls(self):
        return [
            path('fournisseurs/',
                 self.admin_site.admin_view(self.redirect_to_fournisseur_admin),
                name='fournisseurs_admin_link')
        ]

    def redirect_to_fournisseur_admin(self, request):
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(reverse('fournisseur_admin:index'))

    def has_module_permission(self, request):
        return True

admin.site.register(Facture, FournisseursAdminLink)

class FactureResourceSTD(resources.ModelResource):
    beneficiaire = fields.Field(attribute='beneficiaire__raison_sociale', column_name='Beneficiaire')
    contrat = fields.Field(attribute='contrat__numero_contrat', column_name='Contrat')
    moe = fields.Field(attribute='contrat__moe', column_name='MOE')

    class Meta:
        model = Facture
        fields = ('beneficiaire', 'contrat', 'moe', 'num_facture', 'date_facture',
                 'date_echeance', 'montant_ttc', 'mnt_RAS_IS', 'mnt_RAS_TVA',
                 'mnt_RG', 'mnt_net_apayer', 'ordre_virement', 'statut')
        export_order = fields

class FactureResourceDLP(resources.ModelResource):
    # Champs de base
    beneficiaire = fields.Field(attribute='beneficiaire__raison_sociale', column_name='Fournisseur')
    contrat = fields.Field(attribute='contrat__numero_contrat', column_name='Contrat')
    moe = fields.Field(attribute='contrat__moe', column_name='MOE')
    ice = fields.Field(attribute='beneficiaire__code_ice', column_name='ICE')
    rc = fields.Field(attribute='beneficiaire__registre_commerce', column_name='RC')
    echeance_contractuelle = fields.Field(attribute='contrat__mode_paiement', column_name='Echéance contractuelle')
    date_reglement = fields.Field(attribute='ordre_virement__date_remise_banque', column_name='Date règlement')
    
    # Champs calculés
    date_echeance = fields.Field(column_name='Date échéance théorique')
    jours_retard = fields.Field(column_name='Jours de retard (réglé)')
    jours_retard_non_regle = fields.Field(column_name='Jours de retard (non réglé)')
    a_selectionner = fields.Field(column_name='A sélectionner')

    def calculate_echeance(self, date_execution, echeance_contractuelle):
        """Calcule la date d'échéance selon le mode de paiement"""
        if not date_execution or not echeance_contractuelle:
            return None
            
        mode = echeance_contractuelle.upper()
        
        delais = {
            '15J': 15, '30J': 30, '60J': 60, 
            '90J': 90, '120J': 120
        }
        
        if mode in delais:
            return date_execution + relativedelta(days=delais[mode])
        
        if mode.endswith('JFDM'):
            base_delai = mode.replace('JFDM', 'J')
            if base_delai in delais:
                date_plus_delai = date_execution + relativedelta(days=delais[base_delai])
                return date_plus_delai + relativedelta(day=31)
            
        return None

    def get_trimestre_precedent(self):
        """Retourne les dates de début et fin du trimestre précédent"""
        today = date.today()
        mois_en_cours = today.month
        trimestre_en_cours = (mois_en_cours - 1) // 3 + 1
        
        # Calcul du trimestre précédent
        if trimestre_en_cours == 1:
            trimestre_precedent = 4
            annee = today.year - 1
        else:
            trimestre_precedent = trimestre_en_cours - 1
            annee = today.year
        
        # Détermination des mois du trimestre précédent
        premier_mois_trimestre = (trimestre_precedent - 1) * 3 + 1
        dernier_mois_trimestre = premier_mois_trimestre + 2
        
        debut_trimestre = date(annee, premier_mois_trimestre, 1)
        fin_trimestre = date(annee, dernier_mois_trimestre, 1) + relativedelta(day=31)
        
        return debut_trimestre, fin_trimestre

    def is_in_trimestre_precedent(self, date_a_verifier):
        """Vérifie si une date se situe dans le trimestre précédent"""
        if not date_a_verifier:
            return False
            
        debut_trimestre, fin_trimestre = self.get_trimestre_precedent()
        return debut_trimestre <= date_a_verifier <= fin_trimestre

    def calculate_retard(self, date_reference, date_echeance):
        """Calcule le nombre de jours de retard"""
        if not date_reference or not date_echeance:
            return None
        delta = (date_reference - date_echeance).days
        return max(delta, 0)

    def dehydrate_date_echeance(self, facture):
        """Formatte la date d'échéance théorique"""
        try:
            date_exec = facture.date_execution
            echeance_contract = facture.contrat.mode_paiement if facture.contrat else '60J'
            
            date_echeance = self.calculate_echeance(date_exec, echeance_contract)
            return date_echeance.strftime('%d/%m/%Y') if date_echeance else "NA"
        except:
            return "Erreur"

    def dehydrate_jours_retard(self, facture):
        """Calcule le retard pour les factures réglées"""
        try:
            if not facture.ordre_virement or not facture.ordre_virement.date_remise_banque:
                return "FNReglée"
            
            date_echeance = self.calculate_echeance(
                facture.date_execution,
                facture.contrat.mode_paiement if facture.contrat else '60J'
            )
            
            if not date_echeance:
                return "Echéance invalide"
            
            debut_trimestre, fin_trimestre = self.get_trimestre_precedent()
            date_reglement = facture.ordre_virement.date_remise_banque
            
            # Règlement non effectué ou effectué après la fin du trimestre précédent
            if date_reglement > fin_trimestre:
                date_reference = fin_trimestre
            else:
                # Règlement effectué durant le trimestre précédent
                if date_echeance >= debut_trimestre and date_echeance <= fin_trimestre:
                    date_reference = date_reglement
                else:
                    date_reference = debut_trimestre
            
            retard = self.calculate_retard(date_reference, date_echeance)
            return str(retard) if retard is not None else "NA"
        except:
            return "Erreur"

    def dehydrate_jours_retard_non_regle(self, facture):
        """Calcule le retard pour les factures non réglées"""
        try:
            if facture.ordre_virement and facture.ordre_virement.date_remise_banque:
                return "FReglée"
            
            date_echeance = self.calculate_echeance(
                facture.date_execution,
                facture.contrat.mode_paiement if facture.contrat else '60J'
            )
            
            if not date_echeance:
                return "Echéance invalide"
            
            _, fin_trimestre = self.get_trimestre_precedent()
            retard = self.calculate_retard(fin_trimestre, date_echeance)
            
            return str(retard)
        except:
            return "Erreur"

    def dehydrate_a_selectionner(self, facture):
        """Détermine si la facture doit être sélectionnée (1) ou non (0)"""
        try:
            debut_trimestre, fin_trimestre = self.get_trimestre_precedent()
            
            # Vérifie la date de réalisation
            date_realisation = facture.date_execution
            if date_realisation and debut_trimestre <= date_realisation <= fin_trimestre:
                return "1"
            
            # Vérifie la date de règlement
            if facture.ordre_virement and facture.ordre_virement.date_remise_banque:
                date_reglement = facture.ordre_virement.date_remise_banque
                if debut_trimestre <= date_reglement <= fin_trimestre:
                    return "1"
            
            return "0"
        except:
            return "Erreur"

    class Meta:
        model = Facture
        fields = (
            'moe', 'contrat', 'date_facture', 'num_facture', 'montant_ht',
            'montant_ttc', 'beneficiaire', 'ice', 'rc', 'date_execution',
            'echeance_contractuelle', 'date_reglement', 'mnt_net_apayer',
            'date_echeance', 'jours_retard', 'jours_retard_non_regle', 'a_selectionner'
        )
        export_order = fields

class FactureResourceTVA(resources.ModelResource):
    beneficiaire = fields.Field(attribute='beneficiaire__raison_sociale', column_name='Nom Fournisseur')
    ice = fields.Field(attribute='beneficiaire__code_ice', column_name='ICE Fournisseur')
    idf = fields.Field(attribute='beneficiaire__identifiant_fiscale', column_name='IF Fournisseur')
    date_reglement = fields.Field(attribute='ordre_virement__date_remise_banque', column_name='Date Paiement')
    num_facture = fields.Field(attribute='num_facture', column_name='N° Facture')
    date_facture = fields.Field(attribute='date_facture', column_name='Date Facture')
    nature_achat = fields.Field(attribute='nature_achat', column_name='Désignation des biens et services')
    montant_ht = fields.Field(attribute='montant_ht', column_name='Montant HT')
    mnt_tva = fields.Field(attribute='mnt_tva', column_name='Montant TVA')
    montant_ttc = fields.Field(attribute='montant_ttc', column_name='Montant TTC')

    class Meta:
        model = Facture
        fields = ('num_facture', 'date_facture', 'nature_achat', 'beneficiaire', 'idf', 'ice', 'montant_ht',
                 'mnt_tva', 'montant_ttc', 'date_reglement')
        export_order = fields

class EcheanceDateFilter(DateRangeFilter):
    date_field = 'date_echeance'  # Champ de la base de données à filtrer
    title = "Echéance"  # Nom qui apparaît dans la sidebar

class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['beneficiaire'].queryset = Beneficiaire.objects.filter(actif=True).order_by('raison_sociale')

@admin.register(Facture, site=fournisseur_admin)
class FactureAdmin(ExportMixin, admin.ModelAdmin):
    form = FactureForm
    change_list_template = "admin/fournisseurs/facture/change_list.html"

    fields = ('beneficiaire', 'contrat', 'num_facture', 'nature_achat', 'date_facture',
             'date_echeance', 'montant_ht', 'mnt_tva', 'montant_ttc',
             'mnt_RAS_IS', 'mnt_RAS_TVA', 'mnt_RG', 'mnt_net_apayer',
             'proforma_pdf', 'facture_pdf', 'PV_reception_pdf', 'date_execution',
             'ordre_virement', 'statut')

    list_display = ('num_facture', 'beneficiaire', 'contrat', 'montant_ttc',
                   'mnt_net_apayer', 'date_echeance', 'statut')

    search_fields = ('contrat__numero_contrat', 'num_facture', 'beneficiaire__raison_sociale')
    #list_filter = ('statut', 'date_echeance', 'beneficiaire')
    list_filter = (
        EcheanceDateFilter,
        'statut'
    )
    readonly_fields = ('montant_ttc', 'mnt_net_apayer', 'created_by',
                      'updated_by', 'ordre_virement', 'date_paiement', 'statut')
    list_per_page = 25
    list_select_related = ('beneficiaire', 'contrat', 'ordre_virement')
    actions = ["export_std_selected", "export_dlp_selected", "export_tva_selected"]

    class Media:
        js = ('admin/js/jquery.init.js', 'fournisseurs/js/contrat_filter.js')

    def export_std_selected(self, request, queryset):
        return self.process_export(request, FactureResourceSTD(), queryset)

    export_std_selected.short_description = _("Exporter la sélection (Standard)")

    def export_dlp_selected(self, request, queryset):
        return self.process_export(request, FactureResourceDLP(), queryset)

    export_dlp_selected.short_description = _("Exporter la sélection (Délais Paiement)")

    def export_tva_selected(self, request, queryset):
        # Filtrer ici : factures payées le mois précédent
        today = timezone.now().date()
        first_day_this_month = today.replace(day=1)
        last_day_previous_month = first_day_this_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)

        queryset = queryset.filter(
            ordre_virement__date_remise_banque__range=(first_day_previous_month, last_day_previous_month)
        )

        return self.process_export(request, FactureResourceTVA(), queryset)
    
    export_tva_selected.short_description = _("Exporter la sélection (TVA) - mois précédent")

    def process_export(self, request, resource, queryset=None):
        if queryset is None:
            queryset = self.get_queryset(request)

        dataset = resource.export(queryset)
        export_format = request.POST.get('format', 'csv')

        if export_format == 'xlsx':
            export_data = dataset.xlsx
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            file_extension = 'xlsx'
        else:
            export_data = dataset.csv
            content_type = 'text/csv'
            file_extension = 'csv'

        #export_type = 'dlp' if isinstance(resource, FactureResourceDLP) else 'std'
        if isinstance(resource, FactureResourceDLP):
            export_type = 'dlp'
        elif isinstance(resource, FactureResourceTVA):
            export_type = 'tva'
        else:
            export_type = 'std'

        response = HttpResponse(export_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="export_{export_type}_{timezone.now().date()}.{file_extension}"'
        return response

    def get_urls(self):
        urls = super().get_urls()
        # Supprimez la définition de l'URL ici, elle est maintenant dans FournisseurAdminSite
        return urls

    def lien_tableau_bord(self, obj):
        return format_html('<a href="{}" target="_blank">Voir le tableau de bord</a>', "/admin/fournisseurs/tableau_bord_fournisseurs/")

    lien_tableau_bord.short_description = "Tableau de bord"

#@admin.register(Avoir)
@admin.register(Avoir, site=fournisseur_admin)
class AvoirAdmin(admin.ModelAdmin):
    fields = ('num_facture', 'facture_associee', 'date_facture', 'date_echeance',
              'montant_ht', 'mnt_tva', 'montant_ttc', 'mnt_RAS_TVA', 'mnt_RAS_IS',
              'mnt_RG', 'mnt_net_apayer')
    readonly_fields = ('date_echeance', 'montant_ttc', 'mnt_net_apayer')
    list_display = ('num_facture', 'facture_associee', 'montant_ttc', 'date_facture')
    list_select_related = ('facture_associee',)

    def has_import_permission(self, request):
        return request.user.is_superuser