from django.utils import timezone
from datetime import timedelta
from .models import Facture, Paiement

def get_weekly_dashboard_data():
    aujourdhui = timezone.now().date()
    prochains_30_jours = aujourdhui + timedelta(days=30)
    
    # Filtrage principal en Python via les propriétés métier (fact_payee/net_a_payer).
    # Cela évite les expressions ORM sur des propriétés non mappées en base.
    toutes_factures = Facture.objects.select_related('contrat', 'contrat__client', 'paiement').prefetch_related('lignes')
    
    factures_non_soldees = []
    montant_total_du = 0
    montant_echu_retard = 0
    factures_en_retard = []
    previsions_30j = 0

    for f in toutes_factures:
        if not f.fact_payee:
            net_a_payer = f.net_a_payer
            montant_total_du += net_a_payer
            
            # Structure de base pour le template
            fact_data = {
                'numero': f.numero,
                'client': f.contrat.client.nom,
                'date_echeance': f.date_echeance,
                'net_a_payer': net_a_payer,
                'jours_retard': (aujourdhui - f.date_echeance).days if aujourdhui > f.date_echeance else 0
            }
            
            # Factures échues (en retard)
            if f.date_echeance < aujourdhui:
                montant_echu_retard += net_a_payer
                factures_en_retard.append(fact_data)
            # Prévisions de cash à 30 jours (échéance future proche)
            elif aujourdhui <= f.date_echeance <= prochains_30_jours:
                previsions_30j += net_a_payer

    # Tri des retards par le plus grand nombre de jours de retard
    factures_en_retard = sorted(factures_en_retard, key=lambda x: x['jours_retard'], reverse=True)

    # 2. Alertes Écarts de Paiement (solde != 0)
    paiements_anormaux = [
        p for p in Paiement.objects.select_related('client').prefetch_related('factures__lignes')
        if not p.est_solde
    ]

    # Calcul du taux de retard
    taux_retard = (montant_echu_retard / montant_total_du * 100) if montant_total_du > 0 else 0

    return {
        'date_generation': aujourdhui,
        'montant_total_du': montant_total_du,
        'montant_echu_retard': montant_echu_retard,
        'taux_retard': round(taux_retard, 2),
        'previsions_30j': previsions_30j,
        'factures_en_retard': factures_en_retard[:10],  # Top 10
        'paiements_anormaux': paiements_anormaux,
    }