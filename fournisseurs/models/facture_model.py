# models/facture_model.py
from django.db import models
from django.db.models import UniqueConstraint
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

from .audit_model import AuditModel
from .beneficiaire_model import Beneficiaire
from .contrat_model import Contrat
from .ordre_virement_model import OrdreVirement

from fournisseurs.validators import verifier_modifications_autorisees
from fournisseurs.choices import *  # Importer toutes les constantes

class Facture(AuditModel):
    """
    Modèle représentant une facture associée à un bénéficiaire et un contrat.
    """
    beneficiaire = models.ForeignKey(
        Beneficiaire,
        on_delete=models.CASCADE,
        related_name='factures_beneficiaire',
        verbose_name="Bénéficiaire"
    )
    contrat = models.ForeignKey(
        Contrat,
        on_delete=models.PROTECT,
        related_name='factures_contrat',
        verbose_name="Contrat",
        null=True,
        blank=True
    )
    num_facture = models.CharField(max_length=50, verbose_name="Numéro de facture")
    date_facture = models.DateField(verbose_name="Date facture")
    date_echeance = models.DateField(verbose_name="Date d'échéance")
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant TTC")
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant HT")
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant TVA")
    mnt_RAS_TVA = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant RAS TVA", default=0.00)
    mnt_RAS_IS = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant RAS IS", default=0.00)
    mnt_RG = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant RG", default=0.00)
    mnt_net_apayer = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant net à payer", default=0.00)
    proforma_pdf = models.FileField(
        upload_to='proformas/',
        verbose_name="Proforma PDF",
        help_text="Fichier PDF de la facture proforma",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
        ]
    )
    facture_pdf = models.FileField(
        upload_to='factures/',
        verbose_name="Facture PDF",
        help_text="Fichier PDF de la facture",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
        ]
    )
    PV_reception_pdf = models.FileField(
        upload_to='receptions/',
        verbose_name="Reception PDF",
        help_text="Fichier PDF de la reception",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
        ]
    )
    date_execution = models.DateField(verbose_name="Date d'exécution ou de réception",
        null=True,
        blank=True
    )
    ordre_virement = models.ForeignKey(
        OrdreVirement,
        on_delete=models.SET_NULL,
        related_name='factures_ov',
        verbose_name="Ordre de virement",
        null=True,
        blank=True
    )

    date_paiement = models.DateField(verbose_name="Date paiement",
        null=True,
        blank=True
    )

    statut = models.CharField(
        max_length=30,
        choices=STATUT_FAC_CHOICES,
        default='attente',
        verbose_name="Statut de la facture"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beneficiaire', 'num_facture'],
                name='unique_beneficiaire_facture'
            )
        ]

    def update_statut(self):
        """
        Met à jour le statut de la facture en fonction de l'état de l'ordre de virement associé.
        """
        if not self.ordre_virement:
            self.statut = 'attente'
        elif not self.ordre_virement.valide_pour_signature:
            self.statut = 'etablissement'
        elif not self.ordre_virement.remis_a_banque:
            self.statut = 'signature'
        elif not self.ordre_virement.compte_debite:
            self.statut = 'banque'
        else:
            self.statut = 'payee'

    def calculate_montants(self):
        """
        Calcule les montants liés aux retenues et au net à payer.
        """
        if self.contrat:
            self.mnt_RAS_TVA = self.montant_tva * (self.contrat.taux_RAS_TVA / 100)
            self.mnt_RAS_IS = self.montant_ht * (self.contrat.taux_RAS_IS / 100)
            self.mnt_RG = self.montant_ttc * (self.contrat.taux_RG / 100)
            self.mnt_net_apayer = self.montant_ttc - (self.mnt_RAS_TVA + self.mnt_RAS_IS + self.mnt_RG)
        else:
            self.mnt_RAS_TVA = 0
            self.mnt_RAS_IS = 0
            self.mnt_RG = 0
            self.mnt_net_apayer = self.montant_ttc

    def clean(self):
        """
        Validation des données avant sauvegarde.
        """
        if self.montant_ht is None or self.montant_tva is None or self.montant_ttc is None:
            raise ValidationError("Les montants HT, TVA et TTC doivent être renseignés.")

        if self.montant_ttc != (self.montant_ht + self.montant_tva):
            raise ValidationError("Le montant TTC doit être égal à la somme de HT et TVA.")

        if self.contrat and self.beneficiaire != self.contrat.beneficiaire:
            raise ValidationError("Le bénéficiaire de la facture doit correspondre au bénéficiaire du contrat.")

        if not self.proforma_pdf and not self.facture_pdf:
            raise ValidationError("La facture proforma ou définitive doit être téléchargée.")

        if self.contrat and (not self.PV_reception_pdf or not self.date_execution):
            raise ValidationError("Le PV de réception doit être téléchargé et la date exécution renseignée.")

        #Vérifie que le contrat sélectionné appartient bien au bénéficiaire.
        if self.contrat and self.beneficiaire and self.contrat.beneficiaire != self.beneficiaire:
            raise ValidationError("Le contrat sélectionné ne correspond pas au bénéficiaire de la facture.")

        self.valider_modifications_si_virement_encours()

    def save(self, *args, **kwargs):
        """
        Redéfinition de la méthode save pour calculer automatiquement les montants avant la sauvegarde.
        """

        self.calculate_montants()
        self.update_statut()
        super().save(*args, **kwargs)

    def valider_modifications_si_virement_encours(self):
        if self.pk:
            ancienne_instance = Facture.objects.get(pk=self.pk)
            if ancienne_instance.ordre_virement:
                if not self.facture_pdf:
                    champs_modifiables = ['facture_pdf','statut']
                else:
                    champs_modifiables = ['statut']
                verifier_modifications_autorisees(self, ancienne_instance, champs_modifiables)

    def __str__(self):
        return f"Facture {self.num_facture} - {self.beneficiaire.raison_sociale} (Statut: {self.get_statut_display()})"