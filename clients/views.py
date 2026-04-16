from django.shortcuts import render
from django.db.models import Sum, F, Q, Case, When, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta
from .models import Facture, LigneFacture, Client
from fournisseurs.models import Beneficiaire


def dashboard_view(request):
    today = timezone.now().date()
    start_date = (today.replace(day=1) - timedelta(days=365)).replace(day=1)
    end_date = today

    # Annotate each facture with the date to use (paiement or échéance)
    factures = Facture.objects.annotate(
        date_ref=Case(
            When(paiement__date_encaissement__isnull=False, then=F('paiement__date_encaissement')),
            default=F('date_echeance'),
        )
    ).filter(date_ref__gte=start_date, date_ref__lte=end_date)

    # Préparer les expressions pour chaque champ calculé
    montant_tva_expr = ExpressionWrapper(F('base_tva') * F('taux_tva') / 100, output_field=DecimalField(max_digits=12, decimal_places=2))
    montant_ttc_expr = ExpressionWrapper(F('montant_ht') + F('base_tva') * F('taux_tva') / 100, output_field=DecimalField(max_digits=12, decimal_places=2))
    montant_ras_tva_expr = ExpressionWrapper((F('base_tva') * F('taux_tva') / 100) * F('taux_ras_tva') / 100, output_field=DecimalField(max_digits=12, decimal_places=2))
    montant_ras_is_expr = ExpressionWrapper(F('montant_ht') * F('taux_ras_is') / 100, output_field=DecimalField(max_digits=12, decimal_places=2))

    # Par client
    data_clients = (
        LigneFacture.objects
        .filter(facture__in=factures)
        .annotate(
            montant_tva_calc=montant_tva_expr,
            montant_ttc_calc=montant_ttc_expr,
            montant_ras_tva_calc=montant_ras_tva_expr,
            montant_ras_is_calc=montant_ras_is_expr,
        )
        .values(client=F('facture__contrat__client__nom'))
        .annotate(
            montant_ht=Sum('montant_ht'),
            montant_tva=Sum('montant_tva_calc'),
            montant_ttc=Sum('montant_ttc_calc'),
            montant_ras_tva=Sum('montant_ras_tva_calc'),
            montant_ras_is=Sum('montant_ras_is_calc'),
        )
        .order_by('client')
    )

    # Par fournisseur
    data_fournisseurs = (
        LigneFacture.objects
        .filter(facture__in=factures)
        .annotate(
            montant_tva_calc=montant_tva_expr,
            montant_ttc_calc=montant_ttc_expr,
            montant_ras_tva_calc=montant_ras_tva_expr,
            montant_ras_is_calc=montant_ras_is_expr,
        )
        .values(fournisseur=F('facture__contrat__compte_bancaire__beneficiaire__raison_sociale'))
        .annotate(
            montant_ht=Sum('montant_ht'),
            montant_tva=Sum('montant_tva_calc'),
            montant_ttc=Sum('montant_ttc_calc'),
            montant_ras_tva=Sum('montant_ras_tva_calc'),
            montant_ras_is=Sum('montant_ras_is_calc'),
        )
        .order_by('fournisseur')
    )

    context = {
        'data_clients': data_clients,
        'data_fournisseurs': data_fournisseurs,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'clients/dashboard.html', context)
