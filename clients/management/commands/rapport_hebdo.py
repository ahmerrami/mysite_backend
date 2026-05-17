from django.core.management.base import BaseCommand
from clients.services import get_weekly_dashboard_data
from utils.emails import generer_et_envoyer_dashboard_hebdo

class Command(BaseCommand):
    help = "Génère et envoie le tableau de bord hebdomadaire par email"

    def handle(self, *args, **options):
        # Votre code d'exécution ici
        generer_et_envoyer_dashboard_hebdo()
        self.stdout.write(self.style.SUCCESS("Le tableau de bord a été envoyé avec succès !"))