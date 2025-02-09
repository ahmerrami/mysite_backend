# models.py
from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Beneficiaire(models.Model):
    raison_sociale = models.CharField(
        max_length=50,
        verbose_name="Raison sociale",
        help_text="Nom ou raison sociale du bénéficiaire",
        unique=True
    )
    registre_commerce = models.CharField(
        max_length=20,
        verbose_name="Registre du commerce",
        help_text="Numéro de registre du commerce",
        unique=True
    )
    identifiant_fiscale = models.CharField(
        max_length=20,
        verbose_name="Identifiant fiscal",
        help_text="Identifiant fiscal du bénéficiaire",
        unique=True
    )
    code_ice = models.CharField(
        max_length=15,
        verbose_name="Code ICE",
        help_text="Identifiant Commun de l'Entreprise (ICE)",
        unique=True
    )

    def __str__(self):
        return f"{self.id} - {self.raison_sociale} (RC: {self.registre_commerce}, IF: {self.identifiant_fiscale})"


class CompteBancaire(models.Model):
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
        ]
    )
    attestation_rib_pdf = models.FileField(
        upload_to='attestations_rib/',
        verbose_name="Attestation RIB PDF",
        help_text="Fichier PDF de l'attestation RIB",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.banque} - {self.rib} (Bénéficiaire: {self.beneficiaire.raison_sociale})"


class Contrat(models.Model):
    beneficiaire = models.ForeignKey(
        Beneficiaire,
        on_delete=models.CASCADE,
        related_name='contrats',
        verbose_name="Bénéficiaire"
    )
    numero_contrat = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Numéro de contrat"
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
        null=True
    )

    def __str__(self):
        return f"{self.numero_contrat} - {self.objet}"

    def clean(self):
        if self.date_debut > self.date_fin:
            raise ValidationError("La date de début doit être antérieure ou égale à la date de fin.")


class OrdreVirement(models.Model):
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
    valide_pour_paiement = models.BooleanField(default=False)
    OV_signe_pdf = models.FileField(
        upload_to='virements/',
        verbose_name="OV signe PDF",
        help_text="Fichier PDF de l'OV",
        blank=True,
        null=True
    )

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

        if self.compte_bancaire.beneficiaire != self.beneficiaire:
            raise ValidationError(f"Le compte bancaire sélectionné {self.compte_bancaire} doit appartenir au bénéficiaire {self.beneficiaire}.")

class Facture(models.Model):
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
    facture_pdf = models.FileField(
        upload_to='factures/',
        verbose_name="Facture PDF",
        help_text="Fichier PDF de la facture",
        blank=True,
        null=True
    )
    PV_reception_pdf = models.FileField(
        upload_to='receptions/',
        verbose_name="Reception PDF",
        help_text="Fichier PDF de la reception",
        blank=True,
        null=True
    )
    ordre_virement = models.ForeignKey(
        OrdreVirement,
        on_delete=models.CASCADE,
        related_name='factures_ov',
        verbose_name="Ordre de virement",
        null=True,
        blank=True
    )

    def calculate_montants(self):
        """
        Calcule les montants liés aux retenues et au net à payer.
        """
        if self.contrat:
            self.mnt_RAS_TVA = self.montant_tva * (self.contrat.taux_RAS_TVA / 100)
            self.mnt_RAS_IS = self.montant_ht * (self.contrat.taux_RAS_IS / 100)
            self.mnt_RG = self.montant_ht * (self.contrat.taux_RG / 100)
            self.mnt_net_apayer = self.montant_ttc - (self.mnt_RAS_TVA + self.mnt_RAS_IS + self.mnt_RG)

    def clean(self):
        """
        Validation des données avant sauvegarde.
        """
        if self.montant_ttc != (self.montant_ht + self.montant_tva):
            raise ValidationError("Le montant TTC doit être égal à la somme de HT et TVA.")

        if self.contrat and self.beneficiaire != self.contrat.beneficiaire:
            raise ValidationError("Le bénéficiaire de la facture doit correspondre au bénéficiaire du contrat.")

    def save(self, *args, **kwargs):
        """
        Redéfinition de la méthode save pour calculer automatiquement les montants avant la sauvegarde.
        """
        self.calculate_montants()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Facture id {self.id} - Facture {self.num_facture} - {self.beneficiaire.raison_sociale}"


