from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import OperationDiverse, EcritureOperation

@receiver(post_save, sender=EcritureOperation)
@receiver(post_delete, sender=EcritureOperation)
def verifier_equilibre_operation(sender, instance, **kwargs):
    """ Vérifie l'équilibre après chaque ajout ou suppression d'écriture. """
    operation = instance.operation
    if operation.ecritures.exists():  # Vérifier uniquement si des écritures sont présentes
        try:
            operation.valider()  # Vérifie et met `valide = True` si équilibrée
        except ValidationError as e:
            print(f"Validation Error: {e}")
