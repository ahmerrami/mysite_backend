from django.db import models
from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete
from .validators import validate_file_extension
import os
from decouple import config

# Models

class Ville(models.Model):
    ville = models.CharField(max_length=40, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.ville}"

class Periode(models.Model):
    periode = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.periode

# Custom file upload path function
def rename_upload_path(instance, filename, prefix):
    ext = filename.split('.')[-1]
    new_filename = f"{instance.cin}_{instance.nom}_{prefix}.{ext}"
    return os.path.join('stages/', new_filename)

def rename_upload_path_cv(instance, filename):
    return rename_upload_path(instance, filename, 'cv')

def rename_upload_path_lettre(instance, filename):
    return rename_upload_path(instance, filename, 'lettre')

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
    encore_scolarise = models.BooleanField(
        default=False,
        verbose_name="Êtes-vous encore scolarisé(e) ?",
        help_text="Cochez cette case si vous êtes actuellement inscrit dans un établissement d'enseignement"
    )
    selectedPeriode = models.ForeignKey(Periode, on_delete=models.CASCADE, related_name="stages")
    cv = models.FileField(upload_to=rename_upload_path_cv, validators=[validate_file_extension])
    lettre = models.FileField(upload_to=rename_upload_path_lettre, validators=[validate_file_extension])
    isChecked = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False)
    commentaire = models.TextField(null=True, blank=True)

    class Meta:
        permissions = [
            ("can_download", "Can download stage data"),
        ]

    def __str__(self):
        return f"CIN: {self.cin}, Nom: {self.nom}, Date enregistrement: {self.created_at}"

# Signal receiver function
@receiver(post_save, sender=Stage)
def envoyer_email_nouvel_enregistrement(sender, instance, created, **kwargs):
    if created:
        sujet = 'Candidature de stage'
        message = (
            f'Votre demande de stage sur www.supratourstravel.com a été traitée avec succès. Nous vous tiendrons informés de l\'avancement de votre dossier et vous contacterons prochainement.\n\n'
            f'Détails du stage :\n'
            f'Nom : {instance.nom}\n'
            f'Prénom : {instance.prenom}\n'
            f'Ville : {instance.ville}\n'
            f'Email : {instance.email}\n'
            f'Téléphone : {instance.tel}\n'
        )
        destinataires = [instance.email]
        cc_destinataires = []  # Add actual CC recipients if needed
        cci_destinataires = config('CCI_DESTINATAIRES_STAGES', default='').split(',')

        email = EmailMessage(
            sujet,
            message,
            config('AUTHEMAIL_EMAIL_HOST_USER'),
            to=destinataires,
            cc=cc_destinataires,
            bcc=cci_destinataires
        )

        email.send()

# Signal pour supprimer les fichiers liés (cv et lettre) après la suppression d'un Stage
@receiver(post_delete, sender=Stage)
def supprimer_fichiers_stage(sender, instance, **kwargs):
    # Supprime le fichier CV s'il existe
    if instance.cv and os.path.isfile(instance.cv.path):
        os.remove(instance.cv.path)

    # Supprime le fichier lettre s'il existe
    if instance.lettre and os.path.isfile(instance.lettre.path):
        os.remove(instance.lettre.path)

@receiver(pre_save, sender=Stage)
def supprimer_ancien_cv(sender, instance, **kwargs):
    """ Supprime l'ancien CV lorsqu'un nouveau fichier est attaché. """
    if not instance.pk:  # Si c'est une nouvelle instance, ne rien faire
        return

    try:
        ancien_stage = Stage.objects.get(pk=instance.pk)
    except Stage.DoesNotExist:
        return

    # Vérifie si le CV a été modifié
    if ancien_stage.cv and ancien_stage.cv != instance.cv:
        if os.path.isfile(ancien_stage.cv.path):
            os.remove(ancien_stage.cv.path)