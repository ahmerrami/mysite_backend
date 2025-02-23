# models.py
from django.conf import settings
from django.db import models, transaction
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .validators import verifier_modifications_autorisees
from .choices import *  # Importer toutes les constantes

class Beneficiaire(models.Model):
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

    class Meta:
        verbose_name = "Bénéficiaire"
        verbose_name_plural = "Bénéficiaires"
        ordering = ['raison_sociale']

    def __str__(self):
        return f"{self.id} - {self.raison_sociale[:20]} (RC: {self.registre_commerce}, IF: {self.identifiant_fiscale})"


class CompteTresorerie(models.Model):
    """
    Modèle représentant un compte bancaire ou une caisse associé à un bénéficiaire.
    """
    beneficiaire = models.ForeignKey(
        Beneficiaire,
        on_delete=models.CASCADE,
        related_name='comptes',
        verbose_name="Bénéficiaire"
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
        CompteTresorerie,
        on_delete=models.PROTECT,
        related_name='ordres_virements_compte',
        verbose_name="Compte bancaire",
        null=True,
        blank=True
    )
    compte_tresorerie_emetteur = models.ForeignKey(
        CompteTresorerie,
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

class Facture(models.Model):
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
    num_facture = models.CharField(max_length=50, unique=True, verbose_name="Numéro de facture")
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

    statut = models.CharField(
        max_length=30,
        choices=STATUT_FAC_CHOICES,
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
            self.mnt_RG = self.montant_ht * (self.contrat.taux_RG / 100)
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