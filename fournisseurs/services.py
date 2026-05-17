from django.utils import timezone
from datetime import timedelta
from .models import Facture, Contrat


def get_suppliers_invoices_data():
    """Collecte les données des factures impayées des fournisseurs."""
    aujourd_hui = timezone.now().date()
    
    factures = Facture.objects.exclude(statut='payee').select_related('beneficiaire').order_by('date_echeance')
    
    total_montant = sum(f.mnt_net_apayer or 0 for f in factures)
    
    factures_list = []
    for f in factures:
        factures_list.append({
            'num_facture': f.num_facture,
            'beneficiaire': f.beneficiaire.raison_sociale if f.beneficiaire else 'N/A',
            'date_facture': f.date_facture,
            'date_echeance': f.date_echeance,
            'montant': f.mnt_net_apayer or 0,
            'statut': f.statut,
        })
    
    return {
        'date_generation': aujourd_hui,
        'factures': factures_list,
        'total_montant': total_montant,
        'nombre_factures': len(factures_list),
    }


def get_suppliers_overdue_invoices_data():
    """Collecte les données des factures dépassement d'échéance (retard >= 5 jours)."""
    aujourd_hui = timezone.now().date()
    date_limite = aujourd_hui + timedelta(days=5)
    
    factures = Facture.objects.exclude(statut='payee').filter(
        date_echeance__lte=date_limite
    ).select_related('beneficiaire').order_by('date_echeance')
    
    total_montant = sum(f.mnt_net_apayer or 0 for f in factures)
    montant_depassement = sum(
        f.mnt_net_apayer or 0 
        for f in factures 
        if f.date_echeance < aujourd_hui
    )
    
    factures_list = []
    for f in factures:
        jours_retard = (aujourd_hui - f.date_echeance).days if f.date_echeance < aujourd_hui else 0
        factures_list.append({
            'num_facture': f.num_facture,
            'beneficiaire': f.beneficiaire.raison_sociale if f.beneficiaire else 'N/A',
            'date_facture': f.date_facture,
            'date_echeance': f.date_echeance,
            'montant': f.mnt_net_apayer or 0,
            'statut': f.statut,
            'jours_retard': jours_retard,
        })
    
    # Trier par nombre de jours de retard décroissant
    factures_list = sorted(factures_list, key=lambda x: x['jours_retard'], reverse=True)
    
    return {
        'date_generation': aujourd_hui,
        'factures': factures_list[:15],  # Top 15
        'total_montant': total_montant,
        'montant_depassement': montant_depassement,
        'nombre_factures': len(factures_list),
        'taux_depassement': (montant_depassement / total_montant * 100) if total_montant > 0 else 0,
    }


def get_suppliers_unsettled_po_data():
    """Collecte les données des bons de commande non soldés."""
    aujourd_hui = timezone.now().date()
    
    contrats = Contrat.objects.filter(type_contrat='commande').prefetch_related('factures_contrat', 'beneficiaire')
    
    enriched_contrats = []
    total_contrats = 0
    total_factures = 0
    
    for contrat in contrats:
        factures = contrat.factures_contrat.all()
        total_facture = sum(f.montant_ht or 0 for f in factures)
        reste_a_facturer = (contrat.montant_HT or 0) - total_facture
        
        if reste_a_facturer > 0:
            total_contrats += contrat.montant_HT or 0
            total_factures += total_facture
            
            taux_avancement = (total_facture / (contrat.montant_HT or 1) * 100) if contrat.montant_HT else 0
            
            enriched_contrats.append({
                'numero_contrat': contrat.numero_contrat,
                'objet': contrat.objet,
                'beneficiaire': contrat.beneficiaire.raison_sociale if contrat.beneficiaire else 'N/A',
                'montant_HT': contrat.montant_HT or 0,
                'total_facture': total_facture,
                'reste_a_facturer': reste_a_facturer,
                'taux_avancement': round(taux_avancement, 2),
            })
    
    # Trier par reste à facturer décroissant
    enriched_contrats = sorted(enriched_contrats, key=lambda x: x['reste_a_facturer'], reverse=True)
    
    total_reste = total_contrats - total_factures
    
    return {
        'date_generation': aujourd_hui,
        'contrats': enriched_contrats,
        'total_contrats': total_contrats,
        'total_factures': total_factures,
        'total_reste': total_reste,
        'nombre_contrats': len(enriched_contrats),
        'taux_avancement_global': (total_factures / total_contrats * 100) if total_contrats > 0 else 0,
    }
