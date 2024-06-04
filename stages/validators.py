from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
#from django.utils.translation import gettext_lazy as _

RC_REGEX = RegexValidator(r'\d{5}', 'le RC se constitue de 5 chiffres')
TP_REGEX = RegexValidator(r'\d{8}', 'la TP se constitue de 8 chiffres')
IF_REGEX = RegexValidator(r'\d{5}', 'l\'IF se constitue de 7 chiffres')
ICE_REGEX = RegexValidator(r'\d{15}', 'le code ICE se constitue de 15 chiffres')
RIB_REGEX = RegexValidator(r'\d{24}', 'le RIB se constitue de 24 chiffres')
PHONE_REGEX = RegexValidator(r'\d{10}', 'le numéro de téléphone se constitue de 10 chiffres')

def validate_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')