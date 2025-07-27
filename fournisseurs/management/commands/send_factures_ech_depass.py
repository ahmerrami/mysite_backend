# fournisseurs/management/commands/send_factures_ech_depass.py

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.prod")
django.setup()

from django.core.management.base import BaseCommand
from fournisseurs.models.facture_model import Facture
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from decouple import config

class Command(BaseCommand):
    help = "Envoie les factures par email selon un critère."

    def handle(self, *args, **options):
        # Vérifier si nous sommes un jour de week-end (samedi=5, dimanche=6)
        today = datetime.today().weekday()
        if today >= 5:  # 5=samedi, 6=dimanche
            self.stdout.write(self.style.NOTICE("Pas d'envoi des factures le week-end (samedi/dimanche)"))
            return

        today_date = timezone.now().date()
        date_limite = today_date + timedelta(days=5)

        # Récupérer les factures non payées avec échéance dans les 5 jours ou déjà échues
        factures = Facture.objects.exclude(statut='payee').filter(  # ✅ Utilisez exclude()
            date_echeance__lte=date_limite
        ).select_related('beneficiaire').order_by('date_echeance')

        titre = 'Factures à régler en urgence'

        # Préparer les données pour le template
        context = {
            'titre': titre,
            'factures': factures,
            'total': sum(f.mnt_net_apayer for f in factures if f.mnt_net_apayer)
        }

        # Générer le HTML
        html_message = render_to_string('email/factures_impayees.html', context)
        plain_message = strip_tags(html_message)  # Version texte pour les clients mail simples

        # Envoyer l'email
        email = EmailMessage(
            subject="Suivi quotidien des factures impayées déjà échues ou avec échéance dans les 5 prochains jours",
            body=html_message,
            from_email=config('AUTHEMAIL_EMAIL_HOST_USER'),
            to = config('TO_DESTINATAIRES_FACTURES', default='').split(',')
        )
        email.content_subtype = "html"  # Important pour le HTML
        email.send()

        self.stdout.write(self.style.SUCCESS(f"{len(factures)} factures envoyées par email avec succès !"))