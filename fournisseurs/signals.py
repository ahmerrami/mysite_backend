from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.dispatch import receiver

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.dispatch import receiver

from decouple import config

import os
from .models import Facture, OrdreVirement
from .choices import *  # Importer toutes les constantes

User = get_user_model()

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

################################################################################
# Ordre de virement
# Signal pour supprimer les fichiers liés avant la suppression d'un OrdreVirement
@receiver(pre_save, sender=OrdreVirement) ###
def supprimer_anciens_pj_ov(sender, instance, **kwargs):
    """ Supprime l'ancien fichier lorsqu'un nouveau fichier est attaché. """
    if not instance.pk:  # Si c'est une nouvelle instance, ne rien faire
        return

    try:
        old_instance = OrdreVirement.objects.get(pk=instance.pk)
    except OrdreVirement.DoesNotExist:
        return

    # Vérifie si le OV_remis_banque_pdf a été modifié
    if old_instance.OV_remis_banque_pdf and old_instance.OV_remis_banque_pdf != instance.OV_remis_banque_pdf:
        if os.path.isfile(old_instance.OV_remis_banque_pdf.path):
            os.remove(old_instance.OV_remis_banque_pdf.path)

    # Vérifie si le avis_debit_pdf a été modifié
    if old_instance.avis_debit_pdf and old_instance.avis_debit_pdf != instance.avis_debit_pdf:
        if os.path.isfile(old_instance.avis_debit_pdf.path):
            os.remove(old_instance.avis_debit_pdf.path)

# Signal pour mise à jour montant d'un OrdreVirement après son enregistrement
@receiver(post_save, sender=OrdreVirement)
def update_ordre_virement(sender, instance, **kwargs):
    """
    Met à jour le montant de l'ordre de virement après sa création ou modification.
    """
    if kwargs.get('raw', False):
        return
    update_ordre_virement_montant(instance)

    # Si la référence de l'OV est vide, y mettre l'ID
    if not instance.reference:
        instance.reference = str(instance.id+ov_start_num)
        instance.save(update_fields=["reference"])

    # Met à jour la date de paiement des factures associées si OV exécutés
    if instance.compte_debite:
        with transaction.atomic():
            Facture.objects.filter(ordre_virement=instance).update(
                date_paiement=instance.date_operation_banque
            )

@receiver(pre_delete, sender=OrdreVirement)
def remettre_statut_factures_en_attente(sender, instance, **kwargs):
    """
    Remet le statut des factures liées à un ordre de virement à "en attente" après la suppression de l'ordre de virement.
    """
    with transaction.atomic():  # Sécurise les mises à jour en cas d'erreur
        Facture.objects.filter(ordre_virement=instance).update(
            statut="attente",
            date_paiement=None,
            ordre_virement=None  # Optionnel
        )

@receiver(post_delete, sender=OrdreVirement) ###
def supprimer_fichiers_OV(sender, instance, **kwargs):
    # Supprime le fichier OV_remis_banque_pdf s'il existe
    if instance.OV_remis_banque_pdf and os.path.isfile(instance.OV_remis_banque_pdf.path):
        os.remove(instance.OV_remis_banque_pdf.path)

    # Supprime le fichier avis_debit_pdf s'il existe
    if instance.avis_debit_pdf and os.path.isfile(instance.avis_debit_pdf.path):
        os.remove(instance.avis_debit_pdf.path)

################################################################################
# Facture
# Signal pour supprimer les fichiers liés avant la suppression d'un OrdreVirement
@receiver(pre_save, sender=Facture) ###
def supprimer_anciens_pj_facture(sender, instance, **kwargs):
    """ Supprime l'ancien fichier lorsqu'un nouveau fichier est attaché. """
    if not instance.pk:  # Si c'est une nouvelle instance, ne rien faire
        return

    try:
        old_instance = Facture.objects.get(pk=instance.pk)
    except Facture.DoesNotExist:
        return

    # Vérifie si le proforma_pdf a été modifié
    if old_instance.proforma_pdf and old_instance.proforma_pdf != instance.proforma_pdf:
        if os.path.isfile(old_instance.proforma_pdf.path):
            os.remove(old_instance.proforma_pdf.path)

    # Vérifie si le facture_pdf a été modifié
    if old_instance.facture_pdf and old_instance.facture_pdf != instance.facture_pdf:
        if os.path.isfile(old_instance.facture_pdf.path):
            os.remove(old_instance.facture_pdf.path)

    # Vérifie si le PV_reception_pdf a été modifié
    if old_instance.PV_reception_pdf and old_instance.PV_reception_pdf != instance.PV_reception_pdf:
        if os.path.isfile(old_instance.PV_reception_pdf.path):
            os.remove(old_instance.PV_reception_pdf.path)

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

    """ Supprime l'ancien fichier lorsqu'un nouveau fichier est attaché. """
    if not instance.pk:  # Si c'est une nouvelle instance, ne rien faire
        return

    try:
        old_instance = Facture.objects.get(pk=instance.pk)
    except Facture.DoesNotExist:
        return

@receiver(post_save, sender=Facture)
def update_ordre_virement_on_save(sender, instance, **kwargs):
    """
    Met à jour le montant de l'ordre de virement lorsqu'une facture est ajoutée ou modifiée.
    """
    if instance.ordre_virement:
        update_ordre_virement_montant(instance.ordre_virement)

@receiver(pre_delete, sender=Facture)
def notify_users_and_update_ordre_virement(sender, instance, **kwargs):
    """
    1. Met à jour le montant de l'ordre de virement avant suppression
    2. Notifie les utilisateurs created_by et updated_by de la suppression
    """
    # 1. Mise à jour de l'ordre de virement
    if instance.ordre_virement:
        update_ordre_virement_montant(instance.ordre_virement)
    
    # 2. Notification des utilisateurs
    subject = f"Suppression de la facture {instance.num_facture} !!! "
    message = f"La facture {instance.num_facture} dont ci-après détail a été supprimée du système :\n Bénéficiaire : {instance.beneficiaire.raison_sociale}\n Montant TTC : {instance.montant_ttc}\n Echéance : {instance.date_echeance}\n Statut : {instance.statut}"
    
    recipients = set()
    
    # Ajouter created_by s'il existe
    if instance.created_by:
        recipients.add(instance.created_by.email)
    
    # Ajouter updated_by s'il existe et est différent
    if instance.updated_by and instance.updated_by != instance.created_by:
        recipients.add(instance.updated_by.email)
    
    # Envoyer le mail seulement s'il y a des destinataires
    if recipients:
        send_mail(
            subject=subject,
            message=message,
            from_email=config('AUTHEMAIL_EMAIL_HOST_USER'),  # Utilisez DEFAULT_FROM_EMAIL des paramètres
            recipient_list=list(recipients),
            fail_silently=True,
        )
