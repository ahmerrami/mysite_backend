from django.db import models
from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.db.models.signals import post_save
from .validators import validate_file_extension


class Ville(models.Model):
    ville = models.CharField(max_length=15, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.ville

class Periode(models.Model):
    periode = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.periode

class Stage(models.Model):
    civilite = models.CharField(max_length=10)
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    cin = models.CharField(max_length=10, unique=True)
    dateN = models.DateField()
    tel = models.CharField(max_length=10)
    email = models.EmailField()
    adress = models.TextField()
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name="ville_origine")
    niveau = models.CharField(max_length=30)
    ecole = models.CharField(max_length=50)
    specialite = models.CharField(max_length=50)
    villeEcole = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name="ville_ecole")
    selectedPeriode = models.ForeignKey(Periode, on_delete=models.CASCADE, related_name="stages")
    cv = models.FileField(upload_to='uploads/', default=None, validators=[validate_file_extension])
    lettre = models.FileField(upload_to='uploads/', default=None, validators=[validate_file_extension])
    isChecked = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False)
    commentaire = models.TextField(null=True, blank=True)
    #custom_message = models.TextField(null=True, blank=True)

    class Meta:
        permissions = [
            ("can_download", "Can download stage data"),
        ]

    def __str__(self):
        return "CIN: "+self.cin+", Nom: "+self.nom+", Date enregistrement: "+str(self.created_at)


@receiver(post_save, sender=Stage)

def envoyer_email_nouvel_enregistrement(sender, instance, created, **kwargs):
    if created:
        sujet = 'Candidature de stage'
        message = (
            f'Votre demande de stage sur www.supratourstravel.com a été traitée avec succès. Nous vous tiendrons informés de l\'avancement de votre dossier et vous contacterons prochainement.\n\n'
            f'Détails du stage :\n'
            f'Nom : {instance.nom}\n'
            f'Prénom : {instance.prenom}\n'
            f'Email : {instance.email}\n'
            f'Téléphone : {instance.tel}\n'
        )
        destinataires = []  # Remplacez par vos destinataires réels
        destinataires.append(instance.email)  # Ajouter l'email du candidat
        cc_destinataires = []  # Remplacez par vos destinataires réels
        cci_destinataires = ['ahmederrami@gmail.com','y.afekhar@supratourstravel.com']  # Remplacez par vos destinataires réels

        email = EmailMessage(
            sujet,
            message,
            'supratourstravel2009@gmail.com',
            to=destinataires,
            cc=cc_destinataires,
            bcc=cci_destinataires
        )

        email.send()