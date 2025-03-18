import pandas as pd
from django.core.management.base import BaseCommand
from operationsDiverses.models import Compte

class Command(BaseCommand):
    help = "Importe des comptes à partir d'un fichier Excel"

    def add_arguments(self, parser):
        parser.add_argument('fichier_excel', type=str, help="Chemin du fichier Excel à importer")

    def handle(self, *args, **kwargs):
        fichier_excel = kwargs['fichier_excel']
        
        try:
            # Lire le fichier Excel
            df = pd.read_excel(fichier_excel, dtype={'numero': str, 'intitule': str})

            comptes_crees = 0
            for _, row in df.iterrows():
                compte, created = Compte.objects.get_or_create(
                    numero=row['numero'],
                    defaults={'intitule': row['intitule']}
                )
                if created:
                    comptes_crees += 1
            
            self.stdout.write(self.style.SUCCESS(f"Importation terminée : {comptes_crees} comptes créés."))
        
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erreur lors de l'importation : {str(e)}"))
