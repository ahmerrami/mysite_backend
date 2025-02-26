# choices.py

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

STATUT_FAC_CHOICES = [
    ('attente', 'En attente'),
    ('etablissement', 'OV en cours d\'établissement'),
    ('signature', 'OV en cours de signature'),
    ('banque', 'OV remis à la banque'),
    ('payee', 'Facture payée'),
]