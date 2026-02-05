
##settings/dev.py
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
CORS_ALLOWED_ORIGINS = ['http://localhost:5173']

# Configuration MySQL (base de données importée depuis PythonAnywhere)
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

# Configuration spécifique au développement
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Chemin relatif dans le projet
STATIC_ROOT = os.path.join(BASE_DIR, 'static')