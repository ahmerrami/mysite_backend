from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.db import models
from decouple import config
import pandas as pd
from datetime import datetime

from stages10.models import Stage, Ville, Periode, Candidature, Candidat

def export_stages10_by_ville():
    """
    Exporte les données des candidatures de stages10 vers un fichier Excel avec une feuille par ville
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'stages10_par_ville_{timestamp}.xlsx'
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    def make_timezone_naive(df):
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                if hasattr(df[col].dtype, 'tz') and df[col].dtype.tz is not None:
                    df[col] = df[col].dt.tz_localize(None)
        return df

    def prepare_candidature_data(candidatures_queryset):
        data = []
        for c in candidatures_queryset.select_related('candidat','stage','periode','ville'):
            data.append({
                'Nom': c.candidat.nom,
                'Prénom': c.candidat.prenom,
                'Email': c.candidat.email,
                'Téléphone': c.candidat.telephone,
                'Niveau d\'études': c.candidat.niveau_etudes,
                'École': c.candidat.ecole,
                'Stage': c.stage.titre,
                'Période': c.periode.nom,
                'Ville': c.ville.nom,
                'Date de soumission': c.date_soumission,
                'Statut': c.statut,
            })
        df = pd.DataFrame(data)
        return make_timezone_naive(df)

    villes = Ville.objects.all().order_by('nom')
    all_candidatures = Candidature.objects.select_related('candidat','stage','periode','ville').order_by('-date_soumission')
    df_synthese = prepare_candidature_data(all_candidatures)
    df_synthese.to_excel(writer, sheet_name='Synthèse générale', index=False)

    for ville in villes:
        sheet_name = ville.nom[:31].replace('/', '-')
        cands_ville = Candidature.objects.filter(ville=ville).select_related('candidat','stage','periode','ville').order_by('-date_soumission')
        if cands_ville.exists():
            df_ville = prepare_candidature_data(cands_ville)
            df_ville.to_excel(writer, sheet_name=sheet_name, index=False)

    create_stats_sheet(writer)
    writer.close()
    return filename

def create_stats_sheet(writer):
    stats_data = []
    villes_stats = Ville.objects.annotate(nb_candidatures=models.Count('stages')).order_by('-nb_candidatures')
    for ville_stat in villes_stats:
        stats_data.append({
            'Type': 'Par ville',
            'Catégorie': ville_stat.nom,
            'Nombre de candidatures': ville_stat.nb_candidatures
        })
    periodes_stats = Periode.objects.annotate(nb_candidatures=models.Count('stages')).order_by('-nb_candidatures')
    for periode_stat in periodes_stats:
        stats_data.append({
            'Type': 'Par période',
            'Catégorie': periode_stat.nom,
            'Nombre de candidatures': periode_stat.nb_candidatures
        })
    total_candidatures = Candidature.objects.count()
    stats_data.append({'Type': 'Général', 'Catégorie': 'Total candidatures', 'Nombre de candidatures': total_candidatures})
    df_stats = pd.DataFrame(stats_data)
    df_stats.to_excel(writer, sheet_name='Statistiques', index=False)

def send_email_with_attachment(filename, subject, body, to_emails=None):
    # Les destinataires doivent être spécifiés dans le fichier .env via la variable CCI_DESTINATAIRES_STAGES
    # Exemple dans .env : CCI_DESTINATAIRES_STAGES="email1@domaine.com,email2@domaine.com"
    if to_emails is None:
        cci_destinataires = config('CCI_DESTINATAIRES_STAGES', default='').split(',')
        to_emails = [email.strip() for email in cci_destinataires if email.strip()]
        if not to_emails:
            to_emails = ['a.errami@supratourstravel.com']
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=config('AUTHEMAIL_EMAIL_HOST_USER'),
        to=to_emails,
    )
    with open(filename, 'rb') as file:
        email.attach(filename, file.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    email.send()

class Command(BaseCommand):
    help = "Exporte les candidatures de stages10 vers un fichier Excel regroupé par ville et l'envoie par email"
    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            action='append',
            help='Adresse email du destinataire (peut être spécifié plusieurs fois)',
        )
    def handle(self, *args, **options):
        try:
            filename = export_stages10_by_ville()
            self.stdout.write(self.style.SUCCESS('Export des candidatures terminé'))
            recipients = options['email'] if options['email'] else None
            subject = 'Export des candidatures stages10 regroupées par ville'
            body = ("Veuillez trouver ci-joint l'export des candidatures stages10 regroupées par ville.\n\n"
                   "Le classeur contient :\n"
                   "- Une feuille de synthèse générale avec toutes les candidatures\n"
                   "- Une feuille par ville avec les candidatures correspondantes\n"
                   "- Une feuille de statistiques\n\n"
                   "Export généré automatiquement.")
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
