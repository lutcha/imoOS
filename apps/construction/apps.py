"""
Construction App Config.
"""
from django.apps import AppConfig


class ConstructionConfig(AppConfig):
    """Configuração do app Construction."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.construction'
    verbose_name = 'Construção'
    
    def ready(self):
        """Importar signals quando o app estiver pronto."""
        import apps.construction.signals  # noqa
