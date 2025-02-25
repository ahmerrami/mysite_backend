# models/contrat_model.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .beneficiaire_model import Beneficiaire
from ..choices import *  # Importer toutes les constantes

class Contrat(models.Model):
    """
    Modèle représentant un contrat associé à un bénéficiaire.
    """

    beneficiaire = models.ForeignKey(
        Beneficiaire,
        on_delete=models.PROTECT,
        related_name='contrats',
        verbose_name="Bénéficiaire"
    )
    moe = models.CharField(
        max_length=20,
        choices=MOE,
        default='fm',
        verbose_name="Maitrise d'oeuvres",
        help_text="Maitrise d'oeuvres"
    )
    type_contrat = models.CharField(
        max_length=20,
        choices=TYPE_CONTRAT,
        default='marche',
        verbose_name="Type de contrat",
        help_text="Type de contrat"
    )
    numero_contrat = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Numéro de contrat",
        error_messages={
            'unique': _("Ce numéro de contrat est déjà utilisé.")
        }
    )
    objet = models.CharField(max_length=500, verbose_name="Objet")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    mode_paiement = models.CharField(
        max_length=10,
        choices=TYPE_MODE_PAIEMENT,
        default='90JFDM',
        verbose_name="Mode de paiement",
        help_text="Mode de paiement"
    )
    montant_HT = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Montant HT",
        validators=[MinValueValidator(0)]
    )
    taux_de_TVA = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Taux de TVA",
        validators=[MinValueValidator(0), MaxValueValidator(25)]
    )
    taux_RAS_TVA = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Taux RAS TVA",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    taux_RAS_IS = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Taux RAS IS",
        validators=[MinValueValidator(0), MaxValueValidator(40)]
    )
    taux_RG = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Taux RG",
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    contrat_pdf = models.FileField(
        upload_to='contrats/',
        verbose_name="Contrat PDF",
        help_text="Fichier PDF du contrat",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
        ]
    )
    contrat_actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.numero_contrat} - {self.objet[:20]}"

    def clean(self):
        if self.date_debut and self.date_fin and self.date_debut > self.date_fin:
            raise ValidationError("La date de début doit être antérieure ou égale à la date de fin.")
