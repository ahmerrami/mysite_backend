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
    Modèle représentant un compte bancaire, une caisse ou un compte chèque associé à un bénéficiaire.
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
        help_text="Type de compte (bancaire, caisse ou chèque)"
    )

    # === Champs communs / bancaires ===
    banque = models.CharField(
        max_length=50,
        verbose_name="Banque",
        help_text="Nom de la banque (uniquement pour les comptes bancaires ou chèque)",
        blank=True,
        null=True
    )
    rib = models.CharField(
        max_length=24,
        unique=False,
        verbose_name="RIB",
        help_text="Numéro du compte bancaire (uniquement pour les comptes bancaires)",
        validators=[
            RegexValidator(
                regex=r'^\d{24}$',
                message="Le RIB doit contenir exactement 24 chiffres."
            )
        ],
        error_messages={'unique': _("Ce RIB est déjà utilisé.")},
        blank=True,
        null=True
    )

    est_nantissement = models.BooleanField(
        default=False,
        verbose_name="Compte en nantissement",
        help_text="Cochez si ce compte est utilisé pour un nantissement (peut partager le RIB)"
    )

    attestation_rib_pdf = models.FileField(
        upload_to='attestations_rib/',
        verbose_name="Attestation RIB PDF",
        help_text="Fichier PDF de l'attestation RIB (uniquement pour les comptes bancaires)",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )

    # === Champs spécifiques à la caisse ===
    nom_caisse = models.CharField(
        max_length=50,
        verbose_name="Nom de la caisse",
        blank=True,
        null=True
    )
    emplacement_caisse = models.CharField(
        max_length=100,
        verbose_name="Emplacement de la caisse",
        blank=True,
        null=True
    )
    detenteur_caisse = models.CharField(
        max_length=100,
        verbose_name="Détenteur de la caisse",
        blank=True,
        null=True
    )

    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['beneficiaire']

    def clean(self):
        """
        Validation des données avant sauvegarde.
        """
        if self.type_compte == 'bancaire':
            if not self.banque:
                raise ValidationError("Le nom de la banque est obligatoire pour un compte bancaire.")
            if not self.rib:
                raise ValidationError("Le RIB est obligatoire pour un compte bancaire.")

            # Vérification de l'unicité du RIB
            if not self.est_nantissement:
                qs = CompteTresorerie.objects.filter(rib=self.rib, est_nantissement=False)
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    raise ValidationError({"rib": "Ce RIB est déjà utilisé par un autre bénéficiaire (non-nantissement)."})

            # Vérification des ordres de virement
            if self.pk and not self.est_nantissement:
                old_instance = CompteTresorerie.objects.get(pk=self.pk)
                if old_instance.rib != self.rib:
                    if OrdreVirement.objects.filter(compte_tresorerie=old_instance).exists():
                        raise ValidationError(
                            {"rib": "Ce RIB est déjà utilisé dans un ou plusieurs ordres de virement et ne peut pas être modifié."}
                        )

        elif self.type_compte == 'caisse':
            if not self.nom_caisse:
                raise ValidationError("Le nom de la caisse est obligatoire.")
            if not self.emplacement_caisse:
                raise ValidationError("L'emplacement de la caisse est obligatoire.")

        elif self.type_compte == 'cheque':
            # Aucune validation stricte — champ libre, banque facultative
            pass

    def __str__(self):
        if self.type_compte == 'bancaire':
            return f"Banque: {self.banque or 'Inconnue'} - {self.rib or 'RIB non défini'} (Bénéficiaire: {self.beneficiaire.raison_sociale})"
        elif self.type_compte == 'cheque':
            return f"Paiement par chèque ({self.banque or 'Banque non précisée'}) - {self.beneficiaire.raison_sociale}"
        return f"Caisse: {self.nom_caisse or 'Non défini'} ({self.emplacement_caisse or 'Non défini'}) - {self.beneficiaire.raison_sociale}"
