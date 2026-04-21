from django.contrib import admin
from .models import Client, Contrat, Facture, Paiement, LigneFacture
from django import forms
class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("nom", "email", "telephone")
    search_fields = ("nom", "email", "telephone")
    readonly_fields = ('created_by','updated_by')


# Formulaire personnalisé pour Contrat
class ContratForm(forms.ModelForm):
    class Meta:
        model = Contrat
        fields = '__all__'

    class Media:
        js = ('admin/js/contrat_partie_liee.js',)

@admin.register(Contrat)
class ContratAdmin(admin.ModelAdmin):
    form = ContratForm
    list_display = ("reference", "client", "date_signature", "mode_paiement", "taux_ras_tva", "taux_ras_is")
    search_fields = ("reference", "client__nom")
    list_filter = ("mode_paiement",)
    readonly_fields = ('created_by','updated_by')



class EtatFactureListFilter(admin.SimpleListFilter):
    title = "État de paiement"
    parameter_name = "etat_facture"

    def lookups(self, request, model_admin):
        return (
            ("payee", "Payée"),
            ("non_payee", "Non payée"),
        )

    def queryset(self, request, queryset):
        if self.value() == "payee":
            ids = [f.pk for f in queryset.filter(paiement__isnull=False) if f.paiement and f.paiement.est_solde]
            return queryset.filter(pk__in=ids)
        if self.value() == "non_payee":
            ids = [f.pk for f in queryset if not (f.paiement and f.paiement.est_solde)]
            return queryset.filter(pk__in=ids)
        return queryset


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ("contrat", "numero", "date_emission", "date_echeance", "etat_facture")
    search_fields = ("contrat__reference",)
    list_filter = ("date_echeance", EtatFactureListFilter)

    def etat_facture(self, obj):
        if obj.fact_payee:
            return "Payée"
        return "Non payée"
    etat_facture.short_description = "État de paiement"

    def get_readonly_fields(self, request, obj=None):
        base = ('montant_tva','montant_ttc','montant_ras_tva','montant_ras_is','net_a_payer','created_by','updated_by')
        if obj and obj.paiement and obj.paiement.est_solde:
            return base + ('paiement',)
        return base

    inlines = [LigneFactureInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "paiement":
            from .models import Paiement, Facture
            # Récupérer l'ID de la facture depuis l'URL (admin change form)
            facture_id = None
            if request.resolver_match and request.resolver_match.kwargs.get('object_id'):
                try:
                    facture_id = int(request.resolver_match.kwargs['object_id'])
                except Exception:
                    pass
            if facture_id:
                facture = Facture.objects.filter(pk=facture_id).first()
                if facture and facture.paiement and facture.paiement.est_solde:
                    # Paiement soldé : afficher uniquement ce paiement, champ readonly (géré par get_readonly_fields)
                    kwargs["queryset"] = Paiement.objects.filter(pk=facture.paiement.pk)
                    return super().formfield_for_foreignkey(db_field, request, **kwargs)
                # Sinon, filtrage normal
                contrat_id = facture.contrat_id if facture else None
            else:
                contrat_id = None
            if contrat_id:
                client_id = Facture.objects.filter(contrat_id=contrat_id).values_list('contrat__client_id', flat=True).first()
                all_paiements = Paiement.objects.filter(client_id=client_id)
            else:
                all_paiements = Paiement.objects.all()
            non_solde_ids = [p.id for p in all_paiements if not p.est_solde]
            kwargs["queryset"] = Paiement.objects.filter(id__in=non_solde_ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("client", "compte_bancaire", "montant_total", "date_encaissement", "est_solde")
    search_fields = ("client__nom",)
    list_filter = ("date_encaissement",)
    readonly_fields = ('created_by','updated_by')
