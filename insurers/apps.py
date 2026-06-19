from django.apps import AppConfig


class InsurersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'insurers'
    verbose_name = 'Seguradoras e Ramos'

    def ready(self):
        import insurers.signals  # noqa: F401 — registra seed de ramos