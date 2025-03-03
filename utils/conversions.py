# utils/conversions.py
from num2words import num2words

def nombre_en_toutes_lettres(montant):
    partie_entiere = int(montant)
    partie_decimale = round((montant - partie_entiere) * 100)

    texte_entiere = num2words(partie_entiere, lang='fr')
    texte_decimale = num2words(partie_decimale, lang='fr') if partie_decimale > 0 else ""

    montant_en_lettres = f"{texte_entiere.capitalize()} Dirhams"
    if partie_decimale > 0:
        montant_en_lettres += f" et {texte_decimale} Centimes"

    return montant_en_lettres
