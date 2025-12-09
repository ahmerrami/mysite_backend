# settings/prod.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

# Sécurité
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# -------------------------------
# 🔥 BACKUP DIRECT VIA SFTP
# -------------------------------

DBBACKUP_STORAGE = 'storages.backends.sftpstorage.SFTPStorage'
DBBACKUP_STORAGE_OPTIONS = {
    'host': 'ivyerrami.ddns.net',
    'params': {
        'username': 'webmaster',
        'private_key': '/home/supratourstravel/.ssh/id_ed25519',
    },
    'port': 40022,  # Ton port personnalisé
    'path': '/home/webmaster/backups/pythonanywhere/db',  # dossier de stockage DB
}

MEDIABACKUP_STORAGE = 'storages.backends.sftpstorage.SFTPStorage'
MEDIABACKUP_STORAGE_OPTIONS = {
    'host': 'ivyerrami.ddns.net',
    'params': {
        'username': 'webmaster',
        'private_key': '/home/supratourstravel/.ssh/id_ed25519',
    },
    'port': 40022,
    'path': '/home/webmaster/backups/pythonanywhere/media',  # dossier de stockage médias
}

# On ne garde plus rien localement
DBBACKUP_CLEANUP_KEEP = 0
MEDIABACKUP_CLEANUP_KEEP = 0
