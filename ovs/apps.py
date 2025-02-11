from django.apps import AppConfig


class OvsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ovs'

    def ready(self):
        import ovs.signals

