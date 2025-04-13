# mysite/settings/__init__.py
import warnings
import os
from decouple import config

ENV = config('DJANGO_ENV', default='development')

if ENV == 'production':
    from .prod import *
elif ENV == 'development':
    from .dev import *
else:
    warnings.warn(f"Unknown environment {ENV}, using development settings")
    from .dev import *