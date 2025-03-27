from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import datetime
from decimal import Decimal

def validate_annee(value):
    current_year = datetime.date.today().year
    if value not in [current_year, current_year - 1]:
        raise ValidationError(f"L'année doit être {current_year} ou {current_year - 1}.")

class Compte(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    intitule = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.numero} - {self.intitule}"

class OperationDiverse(models.Model):
    libelle = models.TextField(max_length=255)
    date_operation = models.DateField(auto_now_add=True)
    annee_comptable = models.IntegerField(
        default=datetime.date.today().year
    )
    justif_pdf = models.FileField(
        upload_to='operationsDiverses/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    valide = models.BooleanField(default=False)

    def check_equilibre(self):
        """ Vérifie que le total des débits est égal au total des crédits. """
        total_debit = self.ecritures.filter(sens_ecriture='DEBIT').aggregate(models.Sum('montant'))['montant__sum'] or Decimal(0)
        total_credit = self.ecritures.filter(sens_ecriture='CREDIT').aggregate(models.Sum('montant'))['montant__sum'] or Decimal(0)

        if total_debit != total_credit:
            raise ValidationError(f"L'opération doit être équilibrée : Débit {total_debit} ≠ Crédit {total_credit}.")

    def valider(self):
        """ Vérifier et valider définitivement l'opération après toutes les écritures """
        self.check_equilibre()
        self.valide = True
        self.save()

    def save(self, *args, **kwargs):
        """ Sauvegarde sans validation immédiate (pour éviter le problème lors de l'ajout des écritures) """
        super().save(*args, **kwargs)


class EcritureOperation(models.Model):
    OPERATION_TYPE = [
        ('DEBIT', 'Débit'),
        ('CREDIT', 'Crédit')
    ]

    operation = models.ForeignKey(OperationDiverse, on_delete=models.CASCADE, related_name="ecritures")
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=15, decimal_places=2)
    sens_ecriture = models.CharField(max_length=6, choices=OPERATION_TYPE)

    def __str__(self):
        return f"{self.compte} - {self.sens_ecriture} - {self.montant}"
