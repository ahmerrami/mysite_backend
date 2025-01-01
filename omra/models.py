from django.db import models
from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.db.models.signals import post_save
from .validators import validate_file_extension
import os

# Models

# Custom file upload path function
def rename_upload_path(instance, filename, prefix):
    ext = filename.split('.')[-1]
    new_filename = f"{instance.objet}__{prefix}.{ext}"
    return os.path.join('uploads/omra/', new_filename)

def rename_upload_path_omra(instance, filename):
    return rename_upload_path(instance, filename, 'omra')

class Omra(models.Model):
    objet = models.CharField(max_length=15, unique=True)
    date = models.DateField()
    image = models.ImageField(upload_to=rename_upload_path_omra, validators=[validate_file_extension])
    isActive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_download", "Can download omra data"),
        ]

    def __str__(self):
        return f"Objet: {self.objet}, Date : {self.date}"

# Signal receiver function
@receiver(post_save, sender=Omra)
def envoyer_email_nouvel_enregistrement(sender, instance, created, **kwargs):
    if created:
        sujet = 'Nouveau Evenement Omra'
        message = (
            f'Nouveau Evenement Omra publié sur le site supratourstravel.com.\n\n'
            f'Détails de l\'Evenement :\n'
            f'\tObjet : {instance.objet}\n'
            f'\tDate création : {instance.created_at}\n'
            f'\tDate début : {instance.date}\n'
        )
        destinataires = ['t.elaoufir@supratourstravel.com']
        cc_destinataires = ['a.errami@supratourstravel.com']  # Add actual CC recipients if needed
        cci_destinataires = []

        email = EmailMessage(
            sujet,
            message,
            'supratourstravel2009@gmail.com',
            to=destinataires,
            cc=cc_destinataires,
            bcc=cci_destinataires
        )

        email.send()