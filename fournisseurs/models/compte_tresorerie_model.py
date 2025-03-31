# models/compte_tresorerie_model.py
from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .audit_model import AuditModel
from .beneficiaire_model import Beneficiaire
from .ordre_virement_model import OrdreVirement

from fournisseurs.choices import *  # Importer toutes les constantes

class CompteTresorerie(AuditModel):
    """
    Modèle représentant un compte bancaire ou une caisse associé à un bénéficiaire.
    """
    beneficiaire = models.ForeignKey(
        Beneficiaire,
        on_delete=models.CASCADE,
        related_name='comptes',
        verbose_name="Bénéficiaire",
        limit_choices_to={'actif': True}
    )
    type_compte = models.CharField(
        max_length=10,
        choices=TYPE_COMPTE_CHOICES,
        default='bancaire',
        verbose_name="Type de compte",
        help_text="Type de compte (bancaire ou caisse)"
    )
    banque = models.CharField(
        max_length=50,
        verbose_name="Banque",
        help_text="Nom de la banque (uniquement pour les comptes bancaires)",
        blank=True,
        null=True
    )
    rib = models.CharField(
        max_length=24,
        unique=True,
        verbose_name="RIB",
        help_text="Numéro du compte bancaire (uniquement pour les comptes bancaires)",
        validators=[
            RegexValidator(
                regex=r'^\d{24}$',
                message="Le RIB doit contenir exactement 24 chiffres."
            )
        ],
        error_messages={
            'unique': _("Ce RIB est déjà utilisé.")
        },
        blank=True,
        null=True
    )
    attestation_rib_pdf = models.FileField(
        upload_to='attestations_rib/',
        verbose_name="Attestation RIB PDF",
        help_text="Fichier PDF de l'attestation RIB (uniquement pour les comptes bancaires)",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
        ]
    )
    nom_caisse = models.CharField(
        max_length=50,
        verbose_name="Nom de la caisse",
        help_text="Nom de la caisse (uniquement pour les caisses)",
        blank=True,
        null=True
    )
    emplacement_caisse = models.CharField(
        max_length=100,
        verbose_name="Emplacement de la caisse",
        help_text="Emplacement physique de la caisse (uniquement pour les caisses)",
        blank=True,
        null=True
    )
    detenteur_caisse = models.CharField(
        max_length=100,
        verbose_name="Détenteur de la caisse",
        help_text="Détenteur de la caisse (uniquement pour les caisses)",
        blank=True,
        null=True
    )

    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['beneficiaire']

    def __str__(self):
        if self.type_compte == 'bancaire':
            return f"{self.banque or 'Banque inconnue'} - {self.rib or 'RIB non défini'} (Bénéficiaire: {self.beneficiaire.raison_sociale})"
        return f"Caisse: {self.nom_caisse or 'Non défini'} - {self.emplacement_caisse or 'Non défini'} (Bénéficiaire: {self.beneficiaire.raison_sociale})"

    def clean(self):
        """
        Validation des données avant sauvegarde.
        """
        if self.type_compte == 'bancaire':
            if not self.banque:
                raise ValidationError("Le nom de la banque est obligatoire pour un compte bancaire.")
            if not self.rib:
                raise ValidationError("Le RIB est obligatoire pour un compte bancaire.")

            # Vérifiez si le RIB est déjà utilisé dans un ordre de virement
            if self.pk:  # Vérifiez si l'objet existe déjà en base de données
                old_instance = CompteTresorerie.objects.get(pk=self.pk)
                if old_instance.rib != self.rib:  # Le RIB a été modifié
                    if OrdreVirement.objects.filter(compte_tresorerie=old_instance).exists():
                        raise ValidationError(
                            {"rib": "Ce RIB est déjà utilisé dans un ou plusieurs ordres de virement et ne peut pas être modifié."}
                        )

        elif self.type_compte == 'caisse':
            if not self.nom_caisse:
                raise ValidationError("Le nom de la caisse est obligatoire.")
            if not self.emplacement_caisse:
                raise ValidationError("L'emplacement de la caisse est obligatoire.")