from django.core.management.base import BaseCommand

from stages10.models import Candidat
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Supprime les candidats sans candidature après 60 minutes.'

    def handle(self, *args, **options):
        now = timezone.now()
        count = 0
        for candidat in Candidat.objects.all():
            if not candidat.candidatures.exists():
                if now - candidat.date_inscription > timedelta(minutes=60):
                    # Informer le candidat par email avant suppression
                    try:
                        send_mail(
                            'Suppression de votre compte',
                            "Votre compte a été supprimé car vous n'avez pas soumis de candidature dans le délai imparti. Merci de recommencer la procédure si vous souhaitez postuler.",
                            'noreply@exemple.com',
                            [candidat.email],
                            fail_silently=True
                        )
                    except Exception as e:
                        self.stdout.write(f"Erreur lors de l'envoi de l'email à {candidat.email}: {e}")
                    self.stdout.write(f"Suppression du candidat {candidat} (inscrit le {candidat.date_inscription})")
                    candidat.delete()
                    count += 1
        self.stdout.write(self.style.SUCCESS(f"{count} candidat(s) supprimé(s)."))
