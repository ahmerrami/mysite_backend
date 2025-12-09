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
# 🔥 BACKUP DIRECT VIA SFTP (Django Storages)
# -------------------------------

# Configuration Django Storages pour SFTP
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    # Storage pour les backups DB
    "dbbackup": {
        "BACKEND": "storages.backends.sftpstorage.SFTPStorage",
        "OPTIONS": {
            "host": "ivyerrami.ddns.net",
            "params": {
                "username": "webmaster",
                "key_filename": "/home/supratourstravel/.ssh/id_ed25519",
                "port": 40022,  # Port dans params
            },
            "root_path": "/home/webmaster/backups/pythonanywhere/db",
        },
    },
    # Storage pour les backups média
    "mediabackup": {
        "BACKEND": "storages.backends.sftpstorage.SFTPStorage",
        "OPTIONS": {
            "host": "ivyerrami.ddns.net",
            "params": {
                "username": "webmaster",
                "key_filename": "/home/supratourstravel/.ssh/id_ed25519",
                "port": 40022,  # Port dans params
            },
            "root_path": "/home/webmaster/backups/pythonanywhere/media",
        },
    },
}

# Configuration django-dbbackup (nouvelle syntaxe v4+)
DBBACKUP_STORAGE_ALIAS = "dbbackup"
DBBACKUP_MEDIAFILES_STORAGE_ALIAS = "mediabackup"

# Format SQL lisible au lieu de dump binaire
DBBACKUP_CONNECTORS = {
    'default': {
        'CONNECTOR': 'dbbackup.db.mysql.MysqlDumpConnector',
        'DUMP_CMD': 'mysqldump',
        'RESTORE_CMD': 'mysql',
        'DUMP_SUFFIX': '.sql',  # Extension .sql
        'DUMP_PREFIX': 'backup',
    }
}

# On ne garde plus rien localement
DBBACKUP_CLEANUP_KEEP = 0
DBBACKUP_CLEANUP_KEEP_MEDIA = 0
