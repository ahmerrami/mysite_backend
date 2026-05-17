from django.core.management.base import BaseCommand
from django.conf import settings
from utils.emails import generer_et_envoyer_dashboard_hebdo

class Command(BaseCommand):
    help = "Génère et envoie le tableau de bord hebdomadaire par email"

    def handle(self, *args, **options):
        sent_count = generer_et_envoyer_dashboard_hebdo()

        if sent_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    "Aucun email n'a ete envoye. Verifiez EMAIL_BACKEND, la configuration SMTP et les destinataires."
                )
            )
            return

        backend = getattr(settings, 'EMAIL_BACKEND', '')
        if backend == 'django.core.mail.backends.console.EmailBackend':
            self.stdout.write(
                self.style.WARNING(
                    "Email genere avec piece jointe, mais backend console actif: sortie terminal uniquement."
                )
            )
            return

        self.stdout.write(self.style.SUCCESS(f"Le tableau de bord a ete envoye ({sent_count} email)."))