# /fournisseurs/management/commands/send_bc_non_soldes.py
import os
import django
from datetime import datetime

# Initialiser Django si le script est lancé directement
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.prod")
django.setup()

from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from fournisseurs.models.contrat_model import Contrat
from decouple import config

class Command(BaseCommand):
    help = "Envoie un rapport des bons de commande non soldés par email."

    def handle(self, *args, **options):
        # Envoyer une seule fois par semaine
        today = datetime.today().weekday()
        if today != 2:
            self.stdout.write(self.style.NOTICE("Pas d'envoi si pas un mercredi"))
            return

        # Récupération des contrats de type "bon de commande"
        contrats = Contrat.objects.filter(type_contrat='commande') #.prefetch_related('factures_contrat', 'beneficiaire')


        if not contrats.exists():
            self.stdout.write(self.style.NOTICE("Aucun bon de commande non soldé trouvé."))
            return

        total_contrats = 0
        total_factures = 0
        enriched_contrats = []

        for contrat in contrats:
            factures = contrat.factures_contrat.all()
            total_facture = sum(f.montant_ht or 0 for f in factures)
            reste_a_facturer = contrat.montant_HT - total_facture

            if reste_a_facturer:
                total_contrats += contrat.montant_HT
                total_factures += total_facture

                enriched_contrats.append({
                    'numero_contrat': contrat.numero_contrat,
                    'objet': contrat.objet,
                    'beneficiaire': contrat.beneficiaire,
                    'montant_HT': contrat.montant_HT,
                    'total_facture': total_facture,
                    'reste_a_facturer': reste_a_facturer,
                })

        total_reste = total_contrats - total_factures

        context = {
            'contrats': enriched_contrats,
            'total_contrats': total_contrats,
            'total_factures': total_factures,
            'total_reste': total_reste,
        }

        # Rendu du message
        html_message = render_to_string('email/bc_non_soldes.html', context)
        plain_message = strip_tags(html_message)

        # Configuration de l'email
        email = EmailMessage(
            subject="Suivi hebdomadaire des bons de commande non soldés",
            body=html_message,
            from_email=config('AUTHEMAIL_EMAIL_HOST_USER'),
            to = config('TO_DESTINATAIRES_BC', default='').split(',')
        )
        email.content_subtype = "html"
        email.send()

        self.stdout.write(self.style.SUCCESS(f"{len(enriched_contrats)} contrats non soldés envoyés par email avec succès !"))

