from django.db import models
from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.db.models.signals import post_save
from stages.validators import validate_file_extension
import os

# Models

# Custom file upload path function
def rename_upload_path(instance, filename, prefix):
    ext = filename.split('.')[-1]
    new_filename = f"{instance.numero}__{prefix}.{ext}"
    return os.path.join('uploads/aos/', new_filename)

def rename_upload_path_ao(instance, filename):
    return rename_upload_path(instance, filename, 'ao')

class AO(models.Model):
    numero = models.CharField(max_length=16, unique=True)
    objet = models.CharField(max_length=255)
    date = models.DateField()
    aopdf = models.FileField(upload_to=rename_upload_path_ao, validators=[validate_file_extension])
    isActive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_download", "Can download ao data"),
        ]

    def __str__(self):
        return f"Numero: {self.numero}, Objet: {self.objet}, Date : {self.date}"

# Signal receiver function
@receiver(post_save, sender=AO)
def envoyer_email_nouvel_enregistrement(sender, instance, created, **kwargs):
    if created:
        sujet = 'Nouveau AO'
        message = (
            f'Nouveau AO publié sur le site supratourstravel.com.\n\n'
            f'Détails de l\'AO :\n'
            f'\tNuméro : {instance.numero}\n'
            f'\tObjet : {instance.objet}\n'
            f'\tDate création : {instance.created_at}\n'
            f'\tDate Ouverture : {instance.date}\n'
        )
        destinataires = ['c.laabad@supratourstravel.com']
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