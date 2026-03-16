from django.apps import AppConfig


class BranchesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'branches'
    verbose_name = 'Ramos de Seguro'

    def ready(self):
        import branches.signals  # noqa: F401
