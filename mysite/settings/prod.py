#settings/prod.py
from .base import *

# Security
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': '3306',  # Port par défaut pour MySQL
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Configuration spécifique à la production
# Configuration de django-dbbackup
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/home/supratourstravel/backups/'}

# Pour les médias
MEDIABACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIABACKUP_STORAGE_OPTIONS = {'location': '/home/supratourstravel/backups/'}

DBBACKUP_CLEANUP_KEEP = 1   # Conserver 1 backup local (sera transféré vers le serveur)
MEDIABACKUP_CLEANUP_KEEP = 1  # Idem pour les médias
