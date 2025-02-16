# validators.py
from django.core.exceptions import ValidationError

def verifier_modifications_autorisees(instance, ancienne_instance, champs_modifiables):
    """
    Vérifie si des champs non modifiables ont été modifiés.

    :param instance: L'instance du modèle en cours de modification.
    :param ancienne_instance: L'instance actuelle en base de données.
    :param champs_modifiables: Liste des champs autorisés à être modifiés.
    :raises ValidationError: Si un champ non modifiable est modifié.
    """
    for field in instance._meta.fields:
        field_name = field.name
        if field_name not in champs_modifiables:
            ancienne_valeur = getattr(ancienne_instance, field_name)
            nouvelle_valeur = getattr(instance, field_name)
            if ancienne_valeur != nouvelle_valeur:
                raise ValidationError(
                    f"Vous ne pouvez pas modifier le champ '{field_name}' dans cet état."
                )