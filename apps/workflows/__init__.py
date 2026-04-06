"""
Workflows module — Integration & Automation Engine for ImoOS.

Conecta todos os módulos num fluxo contínuo de negócio:
- CRM → Contracts (Lead → Reserva → Contrato)
- Contracts → Construction (Contrato → Projeto de Obra)
- Construction → Payments (Progresso → Pagamentos)
- Notificações automáticas via WhatsApp

Este é um TENANT_APP — cada tenant tem suas próprias definições de workflow.
"""

default_app_config = 'apps.workflows.apps.WorkflowsConfig'
