from django.db import models
from django.conf import settings
from fournisseurs.models import AuditModel, CompteTresorerie, Beneficiaire

class Client(AuditModel):
    id_cpt = models.CharField(max_length=8, unique=True)
    nom = models.CharField(max_length=255)
    adresse = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.nom

class Contrat(AuditModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="client_contrat_created_by"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="client_contrat_updated_by"
    )
    MODES_PAIEMENT = [
        ('virement', 'Virement'),
        ('cheque', 'Chèque'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contrats')
    entite_client = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='avenants')
    reference = models.CharField(max_length=100, unique=True)
    date_signature = models.DateField()
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
    montant_ht = models.DecimalField(max_digits=12, decimal_places=2)
    taux_ras_tva = models.DecimalField(max_digits=5, decimal_places=2, default=75)
    taux_ras_is = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    scan_pdf = models.FileField(upload_to='clients/contrats/', blank=True, null=True, help_text="Scan du contrat (PDF)")
    is_actif = models.BooleanField(default=True)
    is_solde = models.BooleanField(default=False)

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
        is_new = self.pk is None
        super_save = super().save

        # Si c'est un avenant (parent n'est pas None)
        if self.parent is not None:
            self.is_actif = True  # L'avenant est activé
            super_save(*args, **kwargs)
            # Désactiver le contrat père
            Contrat.objects.filter(pk=self.parent.pk).update(is_actif=False)
        else:
            # Si le contrat a au moins un fils (avenant), il doit être désactivé
            if self.avenants.exists():
                self.is_actif = False
            else:
                self.is_actif = True
            super_save(*args, **kwargs)

class Facture(AuditModel):
    numero = models.CharField(max_length=10, unique=True, verbose_name="Numéro de facture")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="client_facture_created_by"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="client_facture_updated_by"
    )
    contrat = models.ForeignKey(
        Contrat,
        on_delete=models.CASCADE,
        related_name='factures',
        limit_choices_to={'is_actif': True,'is_solde': False}
    )
    date_emission = models.DateField()
    date_echeance = models.DateField()
    # Les montants et taux sont désormais gérés par les lignes de facture
    scan_pdf = models.FileField(upload_to='clients/factures/', blank=True, null=True, help_text="Scan de la facture (PDF)")
    paiement = models.ForeignKey(
        'Paiement',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='factures'
    )

    def save(self, *args, **kwargs):
        # Validation : la facture doit être liée à un contrat sans fils (pas d'avenant)
        if self.contrat.avenants.exists():
            raise ValueError("La facture doit être liée à un contrat sans avenant (pas de fils).")
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
    montant_total = models.DecimalField(max_digits=12, decimal_places=2)
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
