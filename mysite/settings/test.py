# settings/test.py
"""
Configuration Django pour les tests
"""
from .base import *

DEBUG = True

# Utiliser une base de données SQLite pour les tests (plus rapide)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Utiliser une BD en mémoire pour les tests
    }
}

# Variables obligatoires pour les tests (sinon elles sont requises depuis l'env)
SOCIETE = 'Test Company'
ALLOWED_HOSTS = ['*']
CORS_ALLOWED_ORIGINS = ['*']
BLOCKED_IPS = []

# Authentification simplifiée pour les tests
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

# Configuration simplifiée pour les tests
MEDIA_ROOT = '/tmp/test_media'
STATIC_ROOT = '/tmp/test_static'

# Désactiver les migrations pour accélérer les tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Email : backend console pour éviter les vrais envois et ne pas nécessiter .env
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'test@example.com'
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
AUTHEMAIL_EMAIL_FROM = 'test@example.com'
AUTHEMAIL_EMAIL_SUBJECT_PREFIX = '[Test] '
AUTHEMAIL_EMAIL_VERIFICATION_URL = '/api/accounts/email/verify/'
AUTHEMAIL_PASSWORD_RESET_URL = '/accounts/password/reset/confirm/'

# Logging minimal pour les tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}

# Désactiver les validations de sécurité pour les tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
