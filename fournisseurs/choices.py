# choices.py

ov_start_num = 8000 # numéro de départ des OV sur cette app

TYPE_COMPTE_CHOICES = [
    ('bancaire', 'Compte bancaire'),
    ('caisse', 'Caisse'),
]

TYPE_CONTRAT = [
    ('marche', 'Marché'),
    ('commande', 'Bon de commande'),
    ('contrat', 'Contrat'),
    ('convention', 'Convention'),
]

TYPE_MODE_PAIEMENT = [
    ('15J', '15 jours'),
    ('30J', '30 jours'),
    ('30JFDM', '30 jours fin de mois'),
    ('60J', '60 jours'),
    ('60JFDM', '60 jours fin de mois'),
    ('90J', '90 jours'),
    ('90JFDM', '90 jours fin de mois'),
    ('120J', '120 jours'),
    ('120JFDM', '120 jours fin de mois'),
]

MOE = [
    ('fm', 'Facility management'),
    ('services', 'Services'),
    ('tourisme', 'Tourisme'),
    ('cfo', 'Front office ONCF'),
    ('support', 'Support'),
]

TYPE_OV_CHOICES = [
    ('Virement', 'Virement'),
    ('Transfert', 'Transfert'),
]

MODE_EXECUTION_OV_CHOICES = [
    ('INDIVIDUEL', 'Individuel'),
    ('MASSE', 'En masse'),
]

STATUT_FAC_CHOICES = [
    ('attente', 'En attente'),
    ('etablissement', 'OV en cours d\'établissement'),
    ('signature', 'OV en cours de signature'),
    ('banque', 'OV remis à la banque'),
    ('payee', 'Facture payée'),
]

NATURE_ACHAT_CHOICES = [
    ('prestations', 'Achat de services'),
    ('travaux', 'Achat de travaux'),
    ('equipement', 'Achat de biens d\'équipement'),
    ('fournitures', 'Achat de fournitures'),
]