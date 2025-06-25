from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.utils.crypto import get_random_string
from django.conf import settings

User = get_user_model()

@receiver(post_save, sender=User)
def send_random_password(sender, instance, created, **kwargs):
    if created:

        # Générer un mot de passe sécurisé
        random_password = get_random_string(length=12)  # Exemple : 12 caractères

        # Définir ce mot de passe pour l'utilisateur
        instance.set_password(random_password)
        instance.save()

        sujet = 'Votre compte a été créé dans idara.supratourstravel.com '
        message = (
            f'Bonjour {instance.email},\n\nVotre compte a été créé avec succès.\n\nVotre mot de passe temporaire est : {random_password}\n\nVeuillez le changer dès votre première connexion.\n\nCordialement,\nL\'équipe.'
        )
        destinataires = [instance.email]
        cc_destinataires = []  # Add actual CC recipients if needed
        cci_destinataires = []

        email = EmailMessage(
            sujet,
            message,
            settings.EMAIL_HOST_USER,
            to=destinataires,
            cc=cc_destinataires,
            bcc=cci_destinataires
        )

        email.send()

