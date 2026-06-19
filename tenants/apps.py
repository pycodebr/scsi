from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenants'
    verbose_name = 'Corretoras'

    def ready(self):
        import tenants.signals  # noqa: F401 — registra seed de Planos