from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import AuditModel
from core.choices import TYPE_MODE_PAIEMENT
from fournisseurs.models import CompteTresorerie
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from calendar import monthrange

class Client(AuditModel):
    id_cpt = models.CharField(max_length=8, unique=True)
    nom = models.CharField(max_length=255)
    adresse = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    # partie_liee indique si le client est une partie liée (filiale, associé, etc.) nécessitant un accord du CA pour les contrats
    partie_liee = models.BooleanField(default=False,verbose_name="Tout contrat nécessite validation",)

    def __str__(self):
        return self.nom

class Contrat(AuditModel):
    MODES_PAIEMENT = [
        ('virement', 'Virement'),
        ('cheque', 'Chèque'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contrats')
    entite_client = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='avenants',verbose_name="Contrat parent ou dernier avenant")
    reference = models.CharField(max_length=100, unique=True)
    date_signature = models.DateField(verbose_name="Date de signature")
    objet = models.CharField(max_length=500, verbose_name="Objet du contrat", null=True, blank=True)
    date_debut = models.DateField(verbose_name="Date de début", null=True, blank=True)
    date_fin = models.DateField(verbose_name="Date de fin", null=True, blank=True)
    delai_paiement = models.CharField(
        max_length=10,
        choices=TYPE_MODE_PAIEMENT,
        default='90JFDM',
        verbose_name="Délai de paiement",
    )
    mode_paiement = models.CharField(max_length=10, choices=MODES_PAIEMENT)
    compte_bancaire = models.ForeignKey(
        CompteTresorerie,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={
            'beneficiaire__raison_sociale': settings.SOCIETE,
            'type_compte': 'bancaire',
        },
        related_name='contrats_encaissement'
    )
    montant_ht = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Montant HT",
    )
    taux_de_TVA = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20,
        verbose_name="Taux de TVA par defaut",
        validators=[MinValueValidator(0), MaxValueValidator(25)]
    )
    taux_ras_tva = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=75,
        verbose_name="Taux de RAS TVA par defaut",
    )
    taux_ras_is = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Taux de RAS IS par defaut",
    )
    scan_pdf = models.FileField(
        upload_to='clients/contrats/',
        blank=True,
        null=True,
        help_text="Scan du contrat (PDF)"
    )
    is_actif = models.BooleanField(
        default=True,
        verbose_name="Contrat actif",
    )
    is_solde = models.BooleanField(
        default=False,
        verbose_name="Contrat soldé",
    )

    # Statut du contrat : autorisé ou non encore validé
    STATUT_CHOICES = [
        ("autorise", "Autorisé"),
        ("non_valide", "Non encore validé"),
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="non_valide")

    # Date d'accord du CA si client partie liée
    date_accord_ca = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Date de l'accord du CA"
    )

    def __str__(self):
        # Construit la chaîne complète de références depuis le contrat racine jusqu'à ce contrat
        chain = []
        contrat = self
        while contrat is not None:
            chain.append(contrat.reference)
            contrat = contrat.parent
        return '-'.join(reversed(chain))

    @property
    def is_avenant(self):
        return self.parent is not None

    def save(self, *args, **kwargs):

        # Validation métier AVANT save
        if self.client and self.client.partie_liee and self.statut == "autorise" and not self.date_accord_ca:
            from django.core.exceptions import ValidationError
            raise ValidationError("La date de l'accord du CA est obligatoire pour les clients parties liées lorsque le contrat est autorisé.")

        # Cas avenant
        if self.parent is not None:
            self.is_actif = True
            super().save(*args, **kwargs)

            # Désactiver le parent
            Contrat.objects.filter(pk=self.parent.pk).update(is_actif=False)

        else:
            # 🔑 IMPORTANT : sauvegarder d'abord pour avoir un PK
            super().save(*args, **kwargs)

            # Maintenant on peut utiliser avenants
            if self.avenants.exists():
                self.is_actif = False
            else:
                self.is_actif = True

            # Mise à jour après logique
            super().save(update_fields=["is_actif"])


class Facture(AuditModel):
    numero = models.CharField(max_length=10, unique=True, verbose_name="Numéro de facture")
    contrat = models.ForeignKey(
        Contrat,
        on_delete=models.CASCADE,
        related_name='factures',
        limit_choices_to={'is_actif': True,'is_solde': False}
    )
    date_realisation = models.DateField(verbose_name="Date de base d'échéance", null=True, blank=True)
    date_emission = models.DateField(verbose_name="Date d'émission")
    date_echeance = models.DateField(verbose_name="Date d'échéance")
    # Les montants et taux sont désormais gérés par les lignes de facture
    scan_pdf = models.FileField(upload_to='clients/factures/', blank=True, null=True, help_text="Scan de la facture (PDF)")
    paiement = models.ForeignKey(
        'Paiement',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='factures'
    )

    @staticmethod
    def _calculate_echeance(date_de_depart, delai_paiement):
        """
        Calcule la date d'échéance basée sur un délai de paiement.
        
        Formats supportés:
        - "15J" : ajoute 15 jours
        - "30JFDM" : ajoute 30 jours et va au dernier jour du mois
        - etc.
        
        Args:
            date_de_depart (date): La date de référence
            delai_paiement (str): Le délai (ex: "30J", "30JFDM", "90JFDM")
            
        Returns:
            date: La date d'échéance calculée
        """
        if not delai_paiement or not date_de_depart:
            return None
            
        if delai_paiement.endswith('JFDM'):
            # Fin de mois : ajouter N jours, puis aller au dernier jour du mois
            jours = int(delai_paiement.replace('JFDM', ''))
            date_temp = date_de_depart + timedelta(days=jours)
            # Récupérer le dernier jour du mois
            last_day = monthrange(date_temp.year, date_temp.month)[1]
            return date_temp.replace(day=last_day)
        elif delai_paiement.endswith('J'):
            # Jours simples
            jours = int(delai_paiement.replace('J', ''))
            return date_de_depart + timedelta(days=jours)
        
        return None

    @property
    def echeance_contractuelle(self):
        """
        Calcule l'échéance contractuelle basée sur :
        - date_realisation si elle est saisie, sinon date_emission
        - le délai de paiement du contrat parent
        
        Returns:
            date: La date d'échéance contractuelle calculée
        """
        date_de_depart = self.date_realisation or self.date_emission
        if not date_de_depart or not self.contrat:
            return None
        return self._calculate_echeance(date_de_depart, self.contrat.delai_paiement)

    def save(self, *args, **kwargs):
        # Validation : la facture doit être liée à un contrat sans fils (pas d'avenant)
        if self.contrat.avenants.exists():
            raise ValueError("La facture doit être liée à un contrat sans avenant (pas de fils).")
        if self.date_echeance != self.echeance_contractuelle:
            raise ValueError("La date d'échéance doit être calculée automatiquement en fonction du contrat et ne peut pas être modifiée manuellement.")
        super().save(*args, **kwargs)

    @property
    def montant_ht(self):
        return sum(l.montant_ht for l in self.lignes.all())

    @property
    def montant_tva(self):
        return sum(l.montant_tva for l in self.lignes.all())

    @property
    def montant_ttc(self):
        return sum(l.montant_ttc for l in self.lignes.all())

    @property
    def montant_ras_tva(self):
        return sum(l.montant_ras_tva for l in self.lignes.all())

    @property
    def montant_ras_is(self):
        return sum(l.montant_ras_is for l in self.lignes.all())

    @property
    def net_a_payer(self):
        return sum(l.net_a_payer for l in self.lignes.all())
    
    @property
    def fact_payee(self):
        return self.paiement and self.paiement.est_solde
    
    def __str__(self):
        return f"Facture {self.numero} - Contrat: {self.contrat}"

# Nouveau modèle LigneFacture
class LigneFacture(models.Model):
    facture = models.ForeignKey('Facture', on_delete=models.CASCADE, related_name='lignes')
    description = models.CharField(max_length=255)
    montant_ht = models.DecimalField(max_digits=12, decimal_places=2)
    base_tva = models.DecimalField(max_digits=12, decimal_places=2, help_text="Montant sur lequel la TVA est appliquée")
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2)
    taux_ras_tva = models.DecimalField(max_digits=5, decimal_places=2)
    taux_ras_is = models.DecimalField(max_digits=5, decimal_places=2)

    @property
    def montant_tva(self):
        return self.base_tva * self.taux_tva / 100

    @property
    def montant_ttc(self):
        return self.montant_ht + self.montant_tva

    @property
    def montant_ras_tva(self):
        return self.montant_tva * self.taux_ras_tva / 100

    @property
    def montant_ras_is(self):
        return self.montant_ht * self.taux_ras_is / 100

    @property
    def net_a_payer(self):
        return self.montant_ttc - self.montant_ras_tva - self.montant_ras_is

class Paiement(AuditModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='paiements')
    compte_bancaire = models.ForeignKey(
        CompteTresorerie,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={
            'beneficiaire__raison_sociale': settings.SOCIETE,
            'type_compte': 'bancaire',
        },
        related_name='paiements_encaissement'
    )
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant total du paiement")
    date_encaissement = models.DateField()

    def __str__(self):
        return f"Paiement {self.id} - {self.client.nom}"

    @property
    def montant_factures(self):
        return sum(f.net_a_payer for f in self.factures.all())

    @property
    def solde(self):
        return self.montant_total - self.montant_factures

    @property
    def est_solde(self):
        return self.montant_total == self.montant_factures
