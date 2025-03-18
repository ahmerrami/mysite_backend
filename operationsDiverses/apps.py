from django.apps import AppConfig


class OperationsdiversesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'operationsDiverses'

    def ready(self):
        import operationsDiverses.signals

