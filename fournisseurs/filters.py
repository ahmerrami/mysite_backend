# filters.py
from django.db.models import Q
from .models import Facture

def get_factures_queryset(beneficiaire_id=None, ordre_virement_id=None):
    """
    Retourne un queryset de factures filtrées en fonction du bénéficiaire et de l'ordre de virement.
    """
    if not beneficiaire_id:
        return Facture.objects.none()

    return Facture.objects.filter(
        Q(beneficiaire_id=beneficiaire_id, ordre_virement__isnull=True) |
        Q(ordre_virement_id=ordre_virement_id)
    )