from django.apps import AppConfig


class CrmConfig(AppConfig):
    name = 'crm'
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'CRM'

    def ready(self):
        import crm.signals  # noqa: F401