from django.apps import AppConfig as appConfig


class AppConfig(appConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        import app.signals
