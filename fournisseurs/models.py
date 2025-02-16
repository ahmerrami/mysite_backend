# models.py
from django.conf import settings
from django.db import models, transaction
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date
from .validators import verifier_modifications_autorisees

class Beneficiaire(models.Model):
    """
    Modèle représentant un bénéficiaire.
    """
    raison_sociale = models.CharField(
        max_length=50,
        verbose_name="Raison sociale",
        help_text="Nom ou raison sociale du bénéficiaire",
        unique=True,
        error_messages={
            'unique': _("Cette raison sociale est déjà utilisée.")
        }
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

    def __str__(self):
        return f"{self.id} - {self.raison_sociale} (RC: {self.registre_commerce}, IF: {self.identifiant_fiscale})"


class CompteBancaire(models.Model):
    """
    Modèle représentant un compte bancaire associé à un bénéficiaire.
    """
    beneficiaire = models.ForeignKey(
        Beneficiaire,
        on_delete=models.CASCADE,
        related_name='comptes_bancaires',
        verbose_name="Bénéficiaire"
    )
    banque = models.CharField(
        max_length=50,
        verbose_name="Banque",
        help_text="Nom de la banque"
    )
    rib = models.CharField(
        max_length=24,
        unique=True,
        verbose_name="RIB",
        help_text="Numéro du compte bancaire",
        validators=[
            RegexValidator(
                regex=r'^\d{24}$',
                message="Le RIB doit contenir exactement 24 chiffres."
            )
        ],
        error_messages={
            'unique': _("Ce RIB est déjà utilisé.")
        }
    )
    attestation_rib_pdf = models.FileField(
        upload_to='attestations_rib/',
        verbose_name="Attestation RIB PDF",
        help_text="Fichier PDF de l'attestation RIB",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
        ]
    )

    def __str__(self):
        return f"{self.banque} - {self.rib} (Bénéficiaire: {self.beneficiaire.raison_sociale})"


class Contrat(models.Model):
    """
    Modèle représentant un contrat associé à un bénéficiaire.
    """
    beneficiaire = models.ForeignKey(
        Beneficiaire,
        on_delete=models.CASCADE,
        related_name='contrats',
        verbose_name="Bénéficiaire"
    )
    numero_contrat = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Numéro de contrat",
        error_messages={
            'unique': _("Ce numéro de contrat est déjà utilisé.")
        }
    )
    objet = models.CharField(max_length=100, verbose_name="Objet")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    montant_TTC = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Montant TTC",
        validators=[MinValueValidator(0)]
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
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    taux_RG = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Taux RG",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
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

    def __str__(self):
        return f"{self.numero_contrat} - {self.objet}"

    def clean(self):
        if self.date_debut > self.date_fin:
            raise ValidationError("La date de début doit être antérieure ou égale à la date de fin.")


class OrdreVirement(models.Model):
    """
    Modèle représentant un ordre de virement.
    """
    TYPE_CHOICES = [
        ('Virement', 'Virement'),
        ('Transfert', 'Transfert'),
    ]
    type_ov = models.CharField(
        max_length=15,
        choices=TYPE_CHOICES,
        verbose_name="Type d'ordre de virement"
    )
    beneficiaire = models.ForeignKey(
        Beneficiaire,
        on_delete=models.CASCADE,
        related_name='ordres_virements',
        verbose_name="Bénéficiaire"
    )
    compte_bancaire = models.ForeignKey(
        CompteBancaire,
        on_delete=models.CASCADE,
        related_name='ordres_virements_compte',
        verbose_name="Compte bancaire"
    )
    compte_bancaire_emetteur = models.ForeignKey(
        CompteBancaire,
        on_delete=models.CASCADE,
        related_name='ordres_virements_emetteur',
        verbose_name="Compte bancaire émetteur"
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

    def __str__(self):
        return f"{self.id} - (Bénéficiaire: {self.beneficiaire.raison_sociale})"

    def clean(self):
        try:
            societe = Beneficiaire.objects.get(raison_sociale=settings.SOCIETE)
        except Beneficiaire.DoesNotExist:
            raise ValidationError("La société dans les paramètres n'existe pas.")

        # Vérifie que le compte bancaire émetteur appartient à la société fixe
        if self.compte_bancaire_emetteur.beneficiaire != societe:
            raise ValidationError("Le compte bancaire émetteur doit appartenir à la société fixe.")

        # Vérifie que le compte bancaire sélectionné appartient au bénéficiaire
        if self.compte_bancaire.beneficiaire != self.beneficiaire:
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

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.valider_modifications_si_remis_a_banque()
            self.mettre_a_jour_remis_a_banque()
            self.mettre_a_jour_statut_factures()
            super().save(*args, **kwargs)

    def valider_modifications_si_remis_a_banque(self):
        if self.pk:
            ancienne_instance = OrdreVirement.objects.get(pk=self.pk)
            if ancienne_instance.remis_a_banque:
                champs_modifiables = ['date_operation_banque']
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
                else:
                    facture.statut = 'banque'
                facture.save()

class Facture(models.Model):
    """
    Modèle représentant une facture associée à un bénéficiaire et un contrat.
    """
    STATUT_CHOICES = [
        ('attente', 'En attente'),
        ('etablissement', 'OV en cours d\'établissement'),
        ('signature', 'OV en cours de signature'),
        ('banque', 'OV remis à la banque'),
    ]

    beneficiaire = models.ForeignKey(
        Beneficiaire,
        on_delete=models.CASCADE,
        related_name='factures_beneficiaire',
        verbose_name="Bénéficiaire"
    )
    contrat = models.ForeignKey(
        Contrat,
        on_delete=models.CASCADE,
        related_name='factures_contrat',
        verbose_name="Contrat",
        null=True,
        blank=True
    )
    num_facture = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
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
    ordre_virement = models.ForeignKey(
        OrdreVirement,
        on_delete=models.SET_NULL,
        related_name='factures_ov',
        verbose_name="Ordre de virement",
        null=True,
        blank=True
    )

    statut = models.CharField(
        max_length=30,
        choices=STATUT_CHOICES,
        default='attente',
        verbose_name="Statut de la facture"
    )

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
        else:
            self.statut = 'banque'

    def calculate_montants(self):
        """
        Calcule les montants liés aux retenues et au net à payer.
        """
        if self.contrat:
            self.mnt_RAS_TVA = self.montant_tva * (self.contrat.taux_RAS_TVA / 100)
            self.mnt_RAS_IS = self.montant_ht * (self.contrat.taux_RAS_IS / 100)
            self.mnt_RG = self.montant_ht * (self.contrat.taux_RG / 100)
            self.mnt_net_apayer = self.montant_ttc - (self.mnt_RAS_TVA + self.mnt_RAS_IS + self.mnt_RG)
        else:
            self.mnt_RAS_TVA = 0
            self.mnt_RAS_IS = 0
            self.mnt_RG = 0
            self.mnt_net_apayer = 0

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

    def save(self, *args, **kwargs):
        """
        Redéfinition de la méthode save pour calculer automatiquement les montants avant la sauvegarde.
        """
        self.calculate_montants()
        self.update_statut()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Facture {self.num_facture} - {self.beneficiaire.raison_sociale} (Statut: {self.get_statut_display()})"