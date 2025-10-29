# sauvgarde_bdd_stages.py

from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.db import models
from decouple import config
import pandas as pd
from datetime import datetime

from stages.models import Stage, Ville, Periode

def export_stages_by_ville():
    """
    Exporte les données des stages vers un fichier Excel avec une feuille par ville
    """
    # Nom du fichier Excel avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'stages_par_ville_{timestamp}.xlsx'

    # Créer un writer Excel
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    def make_timezone_naive(df):
        """Convert timezone-aware datetime columns to naive"""
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                # Si c'est timezone-aware, le rendre naive
                if hasattr(df[col].dtype, 'tz') and df[col].dtype.tz is not None:
                    df[col] = df[col].dt.tz_localize(None)
        return df

    def prepare_stage_data(stages_queryset):
        """Prépare les données des stages pour l'export Excel"""
        stages_data = []
        
        for stage in stages_queryset:
            stages_data.append({
                'CIN': stage.cin,
                'Civilité': stage.civilite,
                'Nom': stage.nom,
                'Prénom': stage.prenom,
                'Date de naissance': stage.dateN,
                'Téléphone': stage.tel,
                'Email': stage.email,
                'Adresse': stage.adress,
                'Ville origine': stage.ville.ville,
                'Niveau': stage.niveau,
                'École': stage.ecole,
                'Spécialité': stage.specialite,
                'Ville école': stage.villeEcole.ville,
                'Période': stage.selectedPeriode.periode,
                'Date création': stage.created_at,
            })
        
        df = pd.DataFrame(stages_data)
        return make_timezone_naive(df)

    # Récupérer toutes les villes qui ont des stages
    villes_avec_stages = Ville.objects.filter(ville_origine__isnull=False).distinct().order_by('ville')
    
    # Feuille de synthèse générale
    all_stages = Stage.objects.select_related('ville', 'villeEcole', 'selectedPeriode').order_by('-created_at')
    df_synthese = prepare_stage_data(all_stages)
    df_synthese.to_excel(writer, sheet_name='Synthèse générale', index=False)
    
    # Feuille par ville
    for ville in villes_avec_stages:
        # Nettoyer le nom de la ville pour le nom de la feuille Excel
        sheet_name = ville.ville[:31]  # Excel limite à 31 caractères
        sheet_name = sheet_name.replace('/', '-')  # Remplacer les caractères invalides
        
        # Récupérer les stages pour cette ville
        stages_ville = Stage.objects.filter(ville=ville).select_related('ville', 'villeEcole', 'selectedPeriode').order_by('-created_at')
        
        if stages_ville.exists():
            df_ville = prepare_stage_data(stages_ville)
            df_ville.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Feuille statistiques
    create_stats_sheet(writer)
    
    # Sauvegarder
    writer.close()
    return filename

def create_stats_sheet(writer):
    """Crée une feuille avec les statistiques des stages"""
    stats_data = []
    
    # Statistiques par ville
    villes_stats = Ville.objects.filter(ville_origine__isnull=False).annotate(
        nb_stages=models.Count('ville_origine')
    ).order_by('-nb_stages')
    
    for ville_stat in villes_stats:
        stats_data.append({
            'Type': 'Par ville',
            'Catégorie': ville_stat.ville,
            'Nombre de stages': ville_stat.nb_stages
        })
    
    # Statistiques par période
    periodes_stats = Periode.objects.annotate(
        nb_stages=models.Count('stages')
    ).order_by('-nb_stages')
    
    for periode_stat in periodes_stats:
        stats_data.append({
            'Type': 'Par période',
            'Catégorie': periode_stat.periode,
            'Nombre de stages': periode_stat.nb_stages
        })
    
    # Statistiques générales
    total_stages = Stage.objects.count()
    
    stats_data.extend([
        {'Type': 'Général', 'Catégorie': 'Total stages', 'Nombre de stages': total_stages},
    ])
    
    df_stats = pd.DataFrame(stats_data)
    df_stats.to_excel(writer, sheet_name='Statistiques', index=False)
def send_email_with_attachment(filename, subject, body, to_emails=None):
    """
    Envoie un email avec le fichier en pièce jointe
    """
    if to_emails is None:
        # Utiliser les destinataires par défaut pour les stages
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

    # Attacher le fichier Excel
    with open(filename, 'rb') as file:
        email.attach(filename, file.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    email.send()


class Command(BaseCommand):
    help = 'Exporte les données des stages vers un fichier Excel regroupé par ville et l\'envoie par email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            action='append',
            help='Adresse email du destinataire (peut être spécifié plusieurs fois)',
        )

    def handle(self, *args, **options):
        try:
            # Importer les models nécessaires pour les statistiques
            from django.db import models
            
            # Exporter les données vers Excel
            filename = export_stages_by_ville()
            self.stdout.write(self.style.SUCCESS('Export des stages par ville terminé'))

            # Déterminer les destinataires
            recipients = options['email'] if options['email'] else None

            # Envoyer par email
            subject = 'Export des stages regroupés par ville'
            body = ('Veuillez trouver ci-joint l\'export des stages regroupés par ville.\n\n'
                   'Le classeur contient :\n'
                   '- Une feuille de synthèse générale avec tous les stages\n'
                   '- Une feuille par ville avec les stages correspondants\n'
                   '- Une feuille de statistiques\n\n'
                   'Export généré automatiquement.')

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