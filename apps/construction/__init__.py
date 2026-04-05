"""
Construction app - ImoOS.

Sistema de gestão de obra com:
- Simple Mode (default): Tasks básicas com status e progresso
- Advanced Mode: CPM (Critical Path Method) e EVM (Earned Value Management)

Integrações:
- WhatsApp (A3): Notificações automáticas
- Budget (A4): Custos estimados e reais
- Projects: Estrutura WBS
"""

default_app_config = 'apps.construction.apps.ConstructionConfig'
