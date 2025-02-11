from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from .models import Facture, OrdreVirement


def update_ordre_virement_montant(ordre_virement):
    """
    Met à jour le montant de l'ordre de virement en fonction du total des factures associées.
    """
    if ordre_virement is None:
        return

    if hasattr(ordre_virement, 'factures_ov'):
        total = ordre_virement.factures_ov.aggregate(total=Sum('mnt_net_apayer'))['total'] or Decimal('0.00')

        # Vérifier si le montant doit être mis à jour
        if ordre_virement.montant != total:

            # Empêcher la boucle infinie en ajoutant un attribut temporaire
            if not hasattr(ordre_virement, '_prevent_signal'):
                ordre_virement._prevent_signal = True

                ordre_virement.montant = total
                ordre_virement.save(update_fields=['montant'])

                del ordre_virement._prevent_signal  # Nettoyer l'attribut


@receiver(post_save, sender=OrdreVirement)
def update_ordre_virement(sender, instance, **kwargs):
    """
    Met à jour le montant de l'ordre de virement après sa création ou modification.
    """
    update_ordre_virement_montant(instance)

@receiver(pre_save, sender=Facture)
def update_ordre_virement_on_change(sender, instance, **kwargs):
    """
    Met à jour l'ancien ordre de virement si la facture change d'affectation.
    """
    if instance.pk:  # Vérifie que la facture existe déjà
        try:
            old_instance = Facture.objects.get(pk=instance.pk)
            if old_instance.ordre_virement and old_instance.ordre_virement != instance.ordre_virement:
                update_ordre_virement_montant(old_instance.ordre_virement)
        except Facture.DoesNotExist:
            pass  # Si la facture n'existe pas encore, rien à faire

@receiver(post_save, sender=Facture)
def update_ordre_virement_on_save(sender, instance, **kwargs):
    """
    Met à jour le montant de l'ordre de virement lorsqu'une facture est ajoutée ou modifiée.
    """
    if instance.ordre_virement:
        update_ordre_virement_montant(instance.ordre_virement)

@receiver(pre_delete, sender=Facture)
def update_ordre_virement_on_delete(sender, instance, **kwargs):
    """
    Met à jour le montant de l'ordre de virement avant qu'une facture soit supprimée.
    """
    if instance.ordre_virement:
        update_ordre_virement_montant(instance.ordre_virement)
