
##settings/dev.py
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
CORS_ALLOWED_ORIGINS = ['http://localhost:5173']

# Configuration MySQL (base de données importée depuis PythonAnywhere)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mysite_pythonanywhere',
        'USER': 'webmaster',
        'PASSWORD': 'pwmysql@2025',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Configuration spécifique au développement
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Chemin relatif dans le projet
STATIC_ROOT = os.path.join(BASE_DIR, 'static')