#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Commande Django: Génère et envoie le rapport des factures impayées aux fournisseurs.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from utils.emails import generer_et_envoyer_factures_impayees_fournisseurs


class Command(BaseCommand):
    help = "Génère et envoie le rapport des factures impayées auprès des fournisseurs par email"

    def handle(self, *args, **options):
        try:
            sent_count = generer_et_envoyer_factures_impayees_fournisseurs()
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Erreur: {str(e)}"))
            return

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
                    "Email genere avec piece jointe, mais backend console actif: sortie terminal uniquement. "
                    "Pour un envoi reel, definir EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend "
                    "et renseigner AUTHEMAIL_EMAIL_HOST, AUTHEMAIL_EMAIL_PORT, "
                    "AUTHEMAIL_EMAIL_HOST_USER, AUTHEMAIL_EMAIL_HOST_PASSWORD, TO_DESTINATAIRES_FACTURES."
                )
            )
            return

        self.stdout.write(self.style.SUCCESS(f"Le rapport factures impayees a ete envoye ({sent_count} email)."))
