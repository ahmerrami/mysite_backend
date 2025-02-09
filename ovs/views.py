# views.py
from django.conf import settings
from django.http import JsonResponse

from .utils import get_factures_queryset
from .models import Beneficiaire, CompteBancaire, Facture

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
