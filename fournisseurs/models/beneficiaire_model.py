# fournisseurs/models/beneficiaire_model.py
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .audit_model import AuditModel

class Beneficiaire(AuditModel):
    """
    Modèle représentant un bénéficiaire.
    """
    raison_sociale = models.CharField(
        max_length=100,
        verbose_name="Raison sociale",
        help_text="Nom ou raison sociale du bénéficiaire",
        unique=True,
        error_messages={
            'unique': _("Cette raison sociale est déjà utilisée.")
        }
    )
    adresse = models.CharField(
        max_length=50,
        verbose_name="Adresse",
        help_text="Adresse du bénéficiaire",
        blank=True,
        null=True
    )
    ville = models.CharField(
        max_length=20,
        verbose_name="Ville",
        help_text="Ville",
        blank=True,
        null=True
    )
    telephone = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Téléphone",
        help_text="Numéro de téléphone",
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Le numéro de téléphone doit contenir exactement 10 chiffres."
            )
        ],
        error_messages={
            'unique': _("Ce numéro de téléphone est déjà utilisé.")
        },
        blank=True,
        null=True
    )
    registre_commerce = models.CharField(
        max_length=20,
        verbose_name="Registre du commerce",
        help_text="Numéro de registre du commerce",
        unique=True,
        error_messages={
            'unique': _("Ce registre du commerce est déjà utilisé.")
        }
    )
    identifiant_fiscale = models.CharField(
        max_length=20,
        verbose_name="Identifiant fiscal",
        help_text="Identifiant fiscal du bénéficiaire",
        unique=True,
        error_messages={
            'unique': _("Cet identifiant fiscal est déjà utilisé.")
        }
    )
    code_ice = models.CharField(
        max_length=15,
        verbose_name="Code ICE",
        help_text="Identifiant Commun de l'Entreprise (ICE)",
        unique=True,
        error_messages={
            'unique': _("Ce code ICE est déjà utilisé.")
        }
    )

    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Bénéficiaire"
        verbose_name_plural = "Bénéficiaires"
        ordering = ['raison_sociale']

    def __str__(self):
        return f"{self.id} - {self.raison_sociale[:20]} (RC: {self.registre_commerce}, IF: {self.identifiant_fiscale})"
