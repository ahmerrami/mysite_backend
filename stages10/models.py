from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class Ville(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nom

class Periode(models.Model):
    nom = models.CharField(max_length=100)
    date_debut = models.DateField()
    date_fin = models.DateField()
    def __str__(self):
        return f"{self.nom} ({self.date_debut} - {self.date_fin})"

class Stage(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    periodes = models.ManyToManyField(Periode, related_name="stages")
    villes = models.ManyToManyField(Ville, related_name="stages")
    actif = models.BooleanField(default=True)
    def __str__(self):
        return self.titre


class Candidat(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    cin = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    email_valide = models.BooleanField(default=False)
    telephone = models.CharField(max_length=20, unique=True)
    telephone_valide = models.BooleanField(default=False)
    niveau_etudes = models.CharField(max_length=100)
    ecole = models.CharField(max_length=150)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.cin})"


class ValidationCode(models.Model):
    TYPE_CHOICES = (
        ("email", "Email"),
        ("sms", "SMS"),
    )
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name="codes")
    code = models.CharField(max_length=6)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)


# Fonctions utilitaires pour renommer les fichiers CV et lettre
import os
def rename_upload_path_candidature(instance, filename, prefix):
    ext = filename.split('.')[-1]
    cin = instance.candidat.cin if hasattr(instance.candidat, 'cin') else 'nocin'
    nom = instance.candidat.nom if hasattr(instance.candidat, 'nom') else 'noname'
    new_filename = f"{cin}_{nom}_{prefix}.{ext}"
    return os.path.join('candidatures/', new_filename)

def rename_upload_path_cv(instance, filename):
    return rename_upload_path_candidature(instance, filename, 'cv')

def rename_upload_path_lettre(instance, filename):
    return rename_upload_path_candidature(instance, filename, 'lettre')


class Candidature(models.Model):
    # Définition des statuts sous forme de classe interne pour une meilleure maintenance
    class Statut(models.TextChoices):
        RECUE = 'RECUE', _('Reçue')
        EXAMEN = 'EXAMEN', _('En cours d\'examen')
        ENTRETIEN = 'ENTRETIEN', _('Entretien planifié')
        OFFRE = 'OFFRE', _('Offre envoyée')
        RETENUE = 'RETENUE', _('Retenue (Recruté)')
        REFUSEE = 'REFUSEE', _('Non retenue')

    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, related_name="candidatures")
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    periode = models.ForeignKey(Periode, on_delete=models.CASCADE)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE)
    
    cv = models.FileField(upload_to=rename_upload_path_cv)
    lettre = models.FileField(upload_to=rename_upload_path_lettre)
    
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True) # Utile pour savoir quand le statut a changé
    
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.RECUE,
    )

    # Champ optionnel mais recommandé pour justifier un refus ou une mise en attente
    commentaire_interne = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Candidature")
        verbose_name_plural = _("Candidatures")
        # On trie par défaut les plus récentes en premier
        ordering = ['-date_soumission']

    def __str__(self):
        return f"{self.candidat} - {self.stage} ({self.get_statut_display()})"