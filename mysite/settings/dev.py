
##settings/dev.py
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
CORS_ALLOWED_ORIGINS = ['http://localhost:5173']

# Configuration SQLite pour le développement local
# Base de données simple et sans dépendances externes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Configuration spécifique au développement
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Chemin relatif dans le projet
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Backend email pour le développement (console - affiche les emails en terminal)
# Aucune connexion SMTP requise, pas d'erreur de réseau
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'