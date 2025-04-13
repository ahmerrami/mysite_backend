
##settings/dev.py
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Configuration SQLite (sans dépendance externe)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Stockée dans le répertoire du projet
    }
}

# Configuration spécifique au développement
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Chemin relatif dans le projet
STATIC_ROOT = os.path.join(BASE_DIR, 'static')