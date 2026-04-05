"""
Budget app config - ImoOS
"""
from django.apps import AppConfig


class BudgetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.budget'
    verbose_name = 'Orçamentos e Preços'
    
    def ready(self):
        """Inicialização do app - verifica feature flag"""
        from django.conf import settings
        
        # Verificar se BUDGET_ENABLED está definido
        self.enabled = getattr(settings, 'BUDGET_ENABLED', True)
        
        if self.enabled:
            # Importar signals se necessário
            pass
