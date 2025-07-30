# /accounts/apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import sys

        # pas de signaux lorsqu'il s'agit de loaddata
        if 'loaddata' in sys.argv or 'migrate' in sys.argv:
            return
        from . import signals