from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core Application"

    def ready(self):
        """
        Import signals when app is ready (safe to leave even if core.signals does not exist).
        """
        try:
            import core.signals  # noqa: F401
        except Exception:
            # No signals file yet — that's fine
            pass
