# views.py
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Sum

import json
from .utils import get_factures_queryset
from .models import Beneficiaire, CompteBancaire, OrdreVirement, Facture

from decimal import Decimal

def get_beneficiaires(request):
    type_ov = request.GET.get('type_ov')
    beneficiaires = Beneficiaire.objects.all()
    societe = Beneficiaire.objects.get(raison_sociale=settings.SOCIETE)

    # Logique de filtrage (à adapter selon votre besoin)
    if type_ov == 'Virement':
        beneficiaires = beneficiaires.exclude(id=societe.id)
    elif type_ov == 'Transfert':
        beneficiaires = beneficiaires.filter(id=societe.id) # Exemple de filtrage
    #Sinon on ne filtre pas les bénéficiaires

    data = {beneficiaire.id: str(beneficiaire) for beneficiaire in beneficiaires}
    return JsonResponse(data)



def get_comptes_bancaires(request):
    beneficiaire_id = request.GET.get('beneficiaire_id')

    if beneficiaire_id is None:
        return JsonResponse({})

    try:
        comptes_bancaires = CompteBancaire.objects.filter(beneficiaire_id=beneficiaire_id)
    except ValueError: #Gérer le cas ou beneficiaire_id n'est pas un entier
        return JsonResponse({})

    data = {compte.id: str(compte) for compte in comptes_bancaires}
    return JsonResponse(data)

def get_factures_all(request):
    beneficiaire_id = request.GET.get('beneficiaire_id')
    ordre_virement_id = request.GET.get('ordre_virement_id')

    factures = get_factures_queryset(beneficiaire_id, ordre_virement_id).values(
        'id', 'num_facture', 'montant_ttc', 'mnt_net_apayer', 'date_echeance', 'ordre_virement'
    )

    return JsonResponse(list(factures), safe=False)

def update_montant_ordre_virement(request, ordre_virement_id):
    try:
        ordre_virement = OrdreVirement.objects.get(id=ordre_virement_id)
        total = ordre_virement.factures_ov.aggregate(total=Sum('mnt_net_apayer'))['total'] or Decimal('0.00')

        # Mise à jour du montant et sauvegarde
        ordre_virement.montant = total
        ordre_virement.save(update_fields=['montant'])

        return JsonResponse({'success': True, 'montant': str(total)})
    except OrdreVirement.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Ordre de virement non trouvé'}, status=404)

@csrf_exempt  # Permet de désactiver la protection CSRF pour cette vue
@require_POST  # S'assure que la vue n'accepte que les requêtes POST
def update_facture_association(request):
    try:
        # Récupérer les données de la requête
        data = json.loads(request.body)
        facture_id = data.get('facture_id')
        ordre_virement_id = data.get('ordre_virement_id')
        is_associated = data.get('is_associated')

        # Valider les données
        if not facture_id or not ordre_virement_id or is_associated is None:
            return JsonResponse(
                {'success': False, 'error': 'Paramètres manquants ou invalides'},
                status=400
            )

        # Récupérer les objets Facture et OrdreVirement
        facture = get_object_or_404(Facture, id=facture_id)
        ordre_virement = get_object_or_404(OrdreVirement, id=ordre_virement_id)

        # Mettre à jour l'association
        if is_associated:
            # Associer la facture à l'ordre de virement
            facture.ordre_virement = ordre_virement
        else:
            # Désassocier la facture de l'ordre de virement
            facture.ordre_virement = None

        # Sauvegarder les modifications
        facture.save()

        # Retourner une réponse JSON en cas de succès
        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'error': 'Données JSON invalides'},
            status=400
        )
    except Facture.DoesNotExist:
        return JsonResponse(
            {'success': False, 'error': 'Facture non trouvée'},
            status=404
        )
    except OrdreVirement.DoesNotExist:
        return JsonResponse(
            {'success': False, 'error': 'Ordre de virement non trouvé'},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': str(e)},
            status=500
        )