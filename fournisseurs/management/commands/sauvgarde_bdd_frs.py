# sauvgarde_bdd_frs.py

from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from decouple import config
import pandas as pd

from fournisseurs.models.beneficiaire_model import Beneficiaire
from fournisseurs.models.compte_tresorerie_model import CompteTresorerie
from fournisseurs.models.contrat_model import Contrat
from fournisseurs.models.facture_model import Facture
from fournisseurs.models.ordre_virement_model import OrdreVirement

def export_multisheet():
    """
    Exporte les données Django vers un fichier Excel avec plusieurs feuilles
    """
    # Nom du fichier Excel
    filename = 'bdd_frs.xlsx'

    # Créer un writer Excel
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    def make_timezone_naive(df):
        """Convert timezone-aware datetime columns to naive"""
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns, UTC]':
                df[col] = df[col].dt.tz_localize(None)
        return df

    # Feuille 1 - Données beneficiaire
    df1 = pd.DataFrame(list(Beneficiaire.objects.all().values()))
    df1 = make_timezone_naive(df1)
    df1 = df1.sort_values('updated_at', ascending=False)
    df1.to_excel(writer, sheet_name='beneficiaires', index=False)

    # Feuille 2 - Données compte tresorerie
    df2 = pd.DataFrame(list(CompteTresorerie.objects.all().values()))
    df2 = make_timezone_naive(df2)
    df2 = df2.sort_values('updated_at', ascending=False)
    df2.to_excel(writer, sheet_name='comptesTresorerie', index=False)

    # Feuille 3 - Données contrat
    df3 = pd.DataFrame(list(Contrat.objects.all().values()))
    df3 = make_timezone_naive(df3)
    df3 = df3.sort_values('updated_at', ascending=False)
    df3.to_excel(writer, sheet_name='contrats', index=False)

    # Feuille 4 - Données facture
    df4 = pd.DataFrame(list(Facture.objects.all().values()))
    df4 = make_timezone_naive(df4)
    df4 = df4.sort_values('updated_at', ascending=False)
    df4.to_excel(writer, sheet_name='factures', index=False)

    # Feuille 5 - Données ordre de virement
    df5 = pd.DataFrame(list(OrdreVirement.objects.all().values()))
    df5 = make_timezone_naive(df5)
    df5 = df5.sort_values('updated_at', ascending=False)
    df5.to_excel(writer, sheet_name='ordresVirement', index=False)

    # Sauvegarder
    writer.close()
    return filename


def send_email_with_attachment(filename, subject, body, to_emails=None):
    """
    Envoie un email avec le fichier en pièce jointe
    """
    if to_emails is None:
        to_emails = ['a.errami@supratourstravel.com','d.naitcheikh@supratourstravel.com']

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=config('AUTHEMAIL_EMAIL_HOST_USER'),
        to=to_emails,
    )

    # Attacher le fichier Excel
    with open(filename, 'rb') as file:
        email.attach(filename, file.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    email.send()


class Command(BaseCommand):
    help = 'Exporte les données des fournisseurs vers un fichier Excel multi-feuilles et l\'envoie par email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            action='append',
            help='Adresse email du destinataire (peut être spécifié plusieurs fois)',
        )

    def handle(self, *args, **options):
        try:
            # Exporter les données vers Excel
            filename = export_multisheet()
            self.stdout.write(self.style.SUCCESS('Export multi-feuilles terminé'))

            # Déterminer les destinataires
            recipients = options['email'] if options['email'] else None

            # Envoyer par email
            subject = 'Export de la base de données fournisseurs'
            body = 'Veuillez trouver ci-joint l\'export de la base de données fournisseurs.'

            send_email_with_attachment(
                filename=filename,
                subject=subject,
                body=body,
                to_emails=recipients
            )

            if recipients:
                self.stdout.write(self.style.SUCCESS(f'Fichier envoyé par email à {", ".join(recipients)}'))
            else:
                self.stdout.write(self.style.SUCCESS('Fichier envoyé par email au destinataire par défaut'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erreur lors de l\'export: {str(e)}'))