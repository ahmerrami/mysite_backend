# models/ordre_virement_model.py
from django.conf import settings
from django.db import models, transaction
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError

from .beneficiaire_model import Beneficiaire
#from .compte_tresorerie_model import CompteTresorerie

from ..validators import verifier_modifications_autorisees
from ..choices import *  # Importer toutes les constantes

class OrdreVirement(models.Model):
    """
    Modèle représentant un ordre de virement.
    """
    reference = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Autre référence de l'ordre de virement si édité sur un autre système",
        null=True,
        blank=True
    )
    type_ov = models.CharField(
        max_length=15,
        choices=TYPE_OV_CHOICES,
        verbose_name="Type d'ordre de virement"
    )
    beneficiaire = models.ForeignKey(
        Beneficiaire,
        on_delete=models.PROTECT,
        related_name='ordres_virements',
        verbose_name="Bénéficiaire"
    )
    compte_tresorerie = models.ForeignKey(
        "fournisseurs.CompteTresorerie",
        on_delete=models.PROTECT,
        related_name='ordres_virements_compte',
        verbose_name="Compte bancaire",
        null=True,
        blank=True
    )
    compte_tresorerie_emetteur = models.ForeignKey(
        "fournisseurs.CompteTresorerie",
        on_delete=models.PROTECT,
        related_name='ordres_virements_emetteur',
        verbose_name="Compte bancaire émetteur",
        null=True,
        blank=True
    )
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Montant",
        validators=[MinValueValidator(0)]
    )
    date_ov = models.DateField(auto_now_add=True, verbose_name="Date de l'ordre de virement")
    valide_pour_signature = models.BooleanField(default=False)
    date_remise_banque = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name="Date remise de l'ordre de virement à la banque")
    OV_remis_banque_pdf = models.FileField(
        upload_to='virements/',
        verbose_name="OV signe PDF",
        help_text="Fichier PDF de l'OV avec AR banque",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
        ]
    )
    remis_a_banque = models.BooleanField(default=False)
    date_operation_banque = models.DateField(auto_now_add=False, null=True, blank=True, verbose_name="Date opération sur relevé bancaire")
    avis_debit_pdf = models.FileField(
        upload_to='avisDebit/',
        verbose_name="avis de débit PDF",
        help_text="Avis de débit",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
        ]
    )
    compte_debite = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - (Bénéficiaire: {self.beneficiaire.raison_sociale})"

    def clean(self):
        try:
            societe = Beneficiaire.objects.get(raison_sociale=settings.SOCIETE)
        except Beneficiaire.DoesNotExist:
            raise ValidationError("La société dans les paramètres n'existe pas.")

        # Vérifie que le compte bancaire émetteur appartient à la société fixe
        if self.compte_tresorerie_emetteur.beneficiaire != societe:
            raise ValidationError("Le compte trésorerie émetteur doit appartenir à la société fixe.")

        # Vérifie que le compte bancaire sélectionné appartient au bénéficiaire
        if self.compte_tresorerie.beneficiaire != self.beneficiaire:
            raise ValidationError(f"Le compte bancaire sélectionné {self.compte_bancaire} doit appartenir au bénéficiaire {self.beneficiaire}.")

        # Vérifie que toutes les factures associées appartiennent au bénéficiaire de l'ordre de virement
        if self.pk:  # Vérifie si l'ordre de virement est déjà enregistré (a un ID)
            factures_associees = self.factures_ov.all()  # Récupère toutes les factures liées à cet ordre de virement
            for facture in factures_associees:
                if facture.beneficiaire != self.beneficiaire:
                    raise ValidationError(
                        f"La facture {facture.num_facture} appartient à un autre bénéficiaire ({facture.beneficiaire.raison_sociale}) "
                        f"que celui de l'ordre de virement ({self.beneficiaire.raison_sociale})."
                    )

        # Vérifie que le virement a été téléchargé et la date remise renseignée avant de cocher la case remis_a_banque
        if self.remis_a_banque == True and ( not self.OV_remis_banque_pdf or not self.date_remise_banque ):
            raise ValidationError("Merci de joindre l'OV signé avec AR de la banque et renseigner la date de remise avant de cocher la case de remise.")

        # Vérifie que l'avis de débit a été téléchargé et la date opération renseignée avant de cocher la case compte_debite
        if self.compte_debite == True and ( not self.avis_debit_pdf or not self.date_operation_banque ):
            raise ValidationError("Merci de joindre l'avis de débit et de renseigner la date de l'opération avant de cocher la case de compte débité.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.valider_modifications_si_remis_a_banque()
            self.mettre_a_jour_remis_a_banque()
            self.valider_modifications_si_compte_debite()
            self.mettre_a_jour_statut_factures()
            super().save(*args, **kwargs)

    def valider_modifications_si_remis_a_banque(self):
        if self.pk:
            ancienne_instance = OrdreVirement.objects.get(pk=self.pk)
            if ancienne_instance.remis_a_banque:
                champs_modifiables = ['remis_a_banque','date_operation_banque','avis_debit_pdf','compte_debite']
                verifier_modifications_autorisees(self, ancienne_instance, champs_modifiables)

    def valider_modifications_si_compte_debite(self):
        if self.pk:
            ancienne_instance = OrdreVirement.objects.get(pk=self.pk)
            if ancienne_instance.compte_debite:
                champs_modifiables = ['avis_debit_pdf','compte_debite']
                verifier_modifications_autorisees(self, ancienne_instance, champs_modifiables)

    def mettre_a_jour_remis_a_banque(self):
        if self.date_remise_banque and self.OV_remis_banque_pdf:
            self.remis_a_banque = True

    def mettre_a_jour_statut_factures(self):
        factures_associees = self.factures_ov.all()
        if factures_associees.exists():
            for facture in factures_associees:
                if not self.valide_pour_signature:
                    facture.statut = 'etablissement'
                elif not self.remis_a_banque:
                    facture.statut = 'signature'
                elif not self.compte_debite:
                    facture.statut = 'banque'
                else:
                    facture.statut = 'payee'
                facture.save()