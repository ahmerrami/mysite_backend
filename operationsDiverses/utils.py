# operationsDivers/utils.py
import pandas as pd
from django.core.exceptions import ValidationError
from .models import Compte

def importer_comptes_excel(fichier_excel):
    try:
        # Lire le fichier Excel
        df = pd.read_excel(fichier_excel, engine="openpyxl")

        # Vérifier que les colonnes nécessaires existent
        if not {'numero', 'intitule'}.issubset(df.columns):
            raise ValidationError("Le fichier Excel doit contenir les colonnes 'numero' et 'intitule'.")

        comptes_crees = []
        for index, row in df.iterrows():
            compte, created = Compte.objects.update_or_create(
                numero=row['numero'],
                defaults={'intitule': row['intitule']}
            )
            if created:
                comptes_crees.append(compte)

        return f"{len(comptes_crees)} comptes importés avec succès."

    except Exception as e:
        return f"Erreur lors de l'importation : {str(e)}"
