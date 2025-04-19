from django.core.management.base import BaseCommand
from fournisseurs.models.facture_model import Facture
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class Command(BaseCommand):
    help = "Envoie les factures par email selon un critère."

    def handle(self, *args, **options):
        # Récupérer les factures non payées avec les relations nécessaires
        factures = Facture.objects.exclude(statut='payee').select_related('beneficiaire')
        
        # Préparer les données pour le template
        context = {
            'factures': factures,
            'total': sum(f.mnt_net_apayer for f in factures if f.mnt_net_apayer)
        }

        # Générer le HTML
        html_message = render_to_string('email/factures_impayees.html', context)
        plain_message = strip_tags(html_message)  # Version texte pour les clients mail simples

        # Envoyer l'email
        email = EmailMessage(
            subject="Liste des factures impayées",
            body=html_message,
            from_email='supratourstravel2009@gmail.com',
            to=['ahmederrami@gmail.com'],
        )
        email.content_subtype = "html"  # Important pour le HTML
        email.send()

        self.stdout.write(self.style.SUCCESS(f"{len(factures)} factures envoyées par email avec succès !"))