from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core Application"

    def ready(self):
        """
        Import signals to ensure they are registered when the app is ready.
        """
        import core.signals