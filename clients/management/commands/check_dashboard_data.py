from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from clients.models import Facture, LigneFacture

class Command(BaseCommand):
    help = 'Affiche les factures et lignes concernées par le dashboard (12 derniers mois)'

    def handle(self, *args, **options):
        today = timezone.now().date()
        start_date = (today.replace(day=1) - timedelta(days=365)).replace(day=1)
        end_date = today

        factures = Facture.objects.annotate(
            date_ref=Case(
                When(paiement__date_encaissement__isnull=False, then=F('paiement__date_encaissement')),
                default=F('date_echeance'),
            )
        ).filter(date_ref__gte=start_date, date_ref__lte=end_date)

        self.stdout.write(f"Factures dans la période : {factures.count()}")
        for f in factures:
            self.stdout.write(f"- Facture #{f.id} | Contrat: {f.contrat} | Date ref: {getattr(f, 'date_ref', f.date_echeance)}")
            lignes = LigneFacture.objects.filter(facture=f)
            self.stdout.write(f"  Lignes: {lignes.count()}")
            for l in lignes:
                self.stdout.write(f"    - {l.description} | HT: {l.montant_ht} | TVA: {l.taux_tva} | RAS TVA: {l.taux_ras_tva} | RAS IS: {l.taux_ras_is}")

        total_lignes = LigneFacture.objects.filter(facture__in=factures).count()
        self.stdout.write(f"Total lignes concernées : {total_lignes}")
