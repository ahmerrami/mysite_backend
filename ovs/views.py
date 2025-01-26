from django.http import JsonResponse
from .models import Beneficiaire, CompteBancaire, Facture

def get_beneficiaires(request):
    type_ov = request.GET.get('type_ov')
    beneficiaires = Beneficiaire.objects.all()

    # Logique de filtrage (à adapter selon votre besoin)
    if type_ov == 'Virement':
        beneficiaires = beneficiaires.exclude(raison_sociale="Supratours Travel")
    elif type_ov == 'Transfert':
        beneficiaires = beneficiaires.filter(raison_sociale="Supratours Travel") # Exemple de filtrage
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


def get_factures_non_affectees(request):
    beneficiaire_id = request.GET.get('beneficiaire_id')
    if beneficiaire_id:
        factures = Facture.objects.filter(
            beneficiaire_id=beneficiaire_id,
            ordre_virement__isnull=True
        ).values('id', 'num_facture', 'montant_ttc', 'date_echeance')
        return JsonResponse(list(factures), safe=False)
    return JsonResponse([], safe=False)
