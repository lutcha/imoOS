# Workflows Module — ImoOS Integration Engine

Módulo de integração e automação de workflows para a plataforma ImoOS.

## Visão Geral

Este módulo conecta todos os módulos do ImoOS num fluxo contínuo de negócio:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         WORKFLOWS IMOOS                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CRM → Contracts → Construction → Payments                              │
│  (A3)    (A4)        (A2)          (A4)                                 │
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │   Lead   │───▶│ Reserva  │───▶│ Contrato │───▶│   Obra   │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│       │               │               │               │                  │
│       ▼               ▼               ▼               ▼                  │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │              NOTIFICAÇÕES (WhatsApp/Email)               │          │
│  └──────────────────────────────────────────────────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Workflows Implementados

### 1. Sales Workflow (Lead → Contrato)

**Arquivo:** `services/sales_workflow.py`

**Fluxo:**
```
Lead Qualificado
    ↓
Reserva de Unidade (48h)
    ↓
Contrato CPV (Promessa)
    ↓
Assinatura Digital
    ↓
Contrato Definitivo
    ↓
Escritura
```

**API Endpoints:**
- `POST /api/workflows/sales/create_reservation/` — Criar reserva
- `POST /api/workflows/sales/create_contract/` — Converter reserva em contrato
- `POST /api/workflows/sales/request_signature/` — Solicitar assinatura
- `POST /api/workflows/sales/mark_signed/` — Marcar como assinado
- `POST /api/workflows/sales/prepare_deed/` — Preparar escritura

### 2. Project Init Workflow (Contrato → Obra)

**Arquivo:** `services/project_init_workflow.py`

**Fluxo:**
```
Contrato Assinado
    ↓
Criar Projeto de Obra
    ↓
Criar Fases (6 fases padrão)
    ↓
Criar Tasks (baseado em templates)
    ↓
Criar Orçamento
    ↓
Notificar Cliente
```

**Fases Padrão:**
1. Fundação (30 dias)
2. Estrutura (60 dias)
3. Alvenaria (45 dias)
4. Instalações MEP (40 dias)
5. Acabamentos (50 dias)
6. Entrega (15 dias)

**API Endpoints:**
- `POST /api/workflows/project-init/initialize/` — Inicializar projeto
- `POST /api/workflows/project-init/import_bim/` — Importar modelo IFC

### 3. Payment Milestone Workflow (Progresso → Pagamentos)

**Arquivo:** `services/payment_milestone_workflow.py`

**Milestones:**
| Fase | Percentagem | Descrição |
|------|-------------|-----------|
| Fundação | 15% | Fundação concluída |
| Estrutura | 25% | Estrutura completa |
| Alvenaria | 15% | Alvenaria concluída |
| MEP | 10% | Instalações concluídas |
| Acabamentos | 25% | Acabamentos finalizados |
| Entrega | 10% | Entrega da unidade |

**Fluxo:**
```
Task Concluída
    ↓
Verificar se é milestone
    ↓
Fase Completa?
    ↓
Gerar Fatura (Prestação)
    ↓
Enviar Notificação
    ↓
Aguardar Pagamento
```

**API Endpoints:**
- `POST /api/workflows/payment-milestones/check_milestone/` — Verificar milestone
- `POST /api/workflows/payment-milestones/reconcile/` — Reconciliar pagamento
- `GET /api/workflows/payment-milestones/schedule/?contract_id=xxx` — Cronograma

### 4. Notification Workflow (Central de Notificações)

**Arquivo:** `services/notification_workflow.py`

**Canais:**
- WhatsApp (primary)
- Email (secondary)
- Push Notification (mobile)

**Eventos:**
- `task_assigned` — Nova tarefa atribuída
- `task_overdue` — Tarefa atrasada
- `payment_due` — Pagamento próximo
- `payment_received` — Pagamento confirmado
- `contract_signed` — Contrato assinado
- `reservation_created` — Reserva confirmada
- `milestone_reached` — Milestone atingido

**API Endpoints:**
- `POST /api/workflows/notifications/send/` — Enviar notificação manual
- `GET /api/workflows/notifications/templates/` — Listar templates

## Signals (Triggers Automáticos)

**Arquivo:** `signals.py`

| Evento | Trigger | Ação |
|--------|---------|------|
| `Lead.status = CONVERTED` | `post_save` | Log para auditoria |
| `UnitReservation.created` | `post_save` | Notificar lead |
| `Contract.status = ACTIVE` | `post_save` | Iniciar projeto de obra |
| `SignatureRequest.created` | `post_save` | Notificar para assinar |
| `SignatureRequest.status = SIGNED` | `post_save` | Ativar contrato |
| `Payment.status = PAID` | `post_save` | Notificar confirmação |
| `ConstructionTask.assigned` | `post_save` | Notificar encarregado |
| `ConstructionTask.completed` | `post_save` | Verificar milestone |
| `ConstructionPhase.completed` | `post_save` | Notificar milestone |

## Celery Tasks

**Arquivo:** `tasks.py`

### Tasks Principais

- `workflows.execute_workflow` — Executar instância de workflow
- `workflows.trigger_project_init_workflow` — Trigger de projeto
- `workflows.trigger_payment_milestone` — Trigger de milestone
- `workflows.send_workflow_notification` — Enviar notificações
- `workflows.check_overdue_tasks` — Verificar tarefas atrasadas (scheduled)
- `workflows.check_upcoming_payments` — Verificar pagamentos (scheduled)

### Configuração Celery Beat

```python
CELERY_BEAT_SCHEDULE = {
    'check-overdue-tasks': {
        'task': 'apps.workflows.tasks.check_overdue_tasks',
        'schedule': 3600.0,  # 1 hora
    },
    'check-upcoming-payments': {
        'task': 'apps.workflows.tasks.check_upcoming_payments',
        'schedule': 86400.0,  # 1 dia
    },
}
```

## Dashboard

**Endpoint:** `GET /api/workflows/dashboard/`

### Estatísticas

- `GET /api/workflows/dashboard/stats/` — Contadores gerais
- `GET /api/workflows/dashboard/active/` — Workflows em execução
- `GET /api/workflows/dashboard/recent_failures/` — Falhas recentes

## Modelos

### WorkflowDefinition

```python
{
    'name': 'Venda Padrão',
    'workflow_type': 'SALES',
    'trigger_event': 'LEAD_CONVERTED',
    'steps_definition': [...],
    'is_active': True,
    'auto_execute': True
}
```

### WorkflowInstance

```python
{
    'workflow': <WorkflowDefinition>,
    'status': 'RUNNING',
    'context': {...},
    'current_step': 2,
    'total_steps': 5,
    'retry_count': 0,
    'max_retries': 3
}
```

### WorkflowStep

```python
{
    'instance': <WorkflowInstance>,
    'order': 1,
    'name': 'Criar Reserva',
    'action_type': 'CREATE_MODEL',
    'action_config': {...},
    'status': 'COMPLETED',
    'result_data': {...}
}
```

## Uso

### Criar Reserva

```python
from apps.workflows.services import SalesWorkflow

result = SalesWorkflow.convert_lead_to_reservation(
    lead_id='uuid-do-lead',
    unit_id='uuid-da-unidade',
    user=request.user,
    deposit_cve=Decimal('50000.00')
)
```

### Inicializar Projeto

```python
from apps.workflows.services import ProjectInitWorkflow

result = ProjectInitWorkflow.create_construction_project(
    contract_id='uuid-do-contrato',
    user=request.user,
    start_date=date(2026, 6, 1)
)
```

### Verificar Milestone

```python
from apps.workflows.services import PaymentMilestoneWorkflow

result = PaymentMilestoneWorkflow.check_payment_milestone(
    task_id='uuid-da-task'
)
```

### Enviar Notificação

```python
from apps.workflows.services import NotificationWorkflow

result = NotificationWorkflow.notify(
    event_type='task_assigned',
    recipient_id='uuid-do-user',
    recipient_type='user',
    data={'task_name': 'Fundação', 'due_date': '2026-06-15'}
)
```

## Testes

```bash
# Testes unitários
pytest apps/workflows/tests/test_sales_workflow.py -v
pytest apps/workflows/tests/test_project_init_workflow.py -v
pytest apps/workflows/tests/test_payment_milestone_workflow.py -v

# Todos os testes de workflows
pytest apps/workflows/tests/ -v
```

## Integrações

### Módulos Integrados

- **CRM (A3):** Leads, Reservas, WhatsApp
- **Contracts (A4):** Contratos, Assinaturas, Pagamentos
- **Construction (A2):** Tasks, Fases, Projetos
- **Payments (A4):** Planos de pagamento, Milestones
- **Inventory:** Unidades, Status
- **Projects:** Empreendimentos, Edifícios

### Próximas Integrações

- **BIM (B1):** Importação IFC, vinculação de elementos
- **Mobile (B2):** Notificações push
- **Dashboard (B3):** Widgets de progresso

## Arquitetura

```
apps/workflows/
├── models.py              # Modelos de workflow
├── services/
│   ├── sales_workflow.py          # Lead → Contrato
│   ├── project_init_workflow.py   # Contrato → Obra
│   ├── payment_milestone_workflow.py  # Progresso → Pagamento
│   └── notification_workflow.py   # Central de notificações
├── signals.py             # Triggers automáticos
├── tasks.py               # Celery tasks
├── views.py               # API endpoints
├── urls.py                # Rotas
└── tests/                 # Testes
```

## Resiliência

- **Graceful Degradation:** Se WhatsApp falhar, continua o workflow
- **Retry Logic:** Até 3 tentativas para cada passo
- **Manual Retry:** Endpoints para re-executar workflows falhados
- **Logging Completo:** Cada passo é logado para auditoria

## Tenant Isolation

Todos os workflows respeitam o isolamento multi-tenant:
- Cada workflow instance pertence a um tenant
- Signals usam o schema atual
- Celery tasks recebem `tenant_schema` como parâmetro
- Queries sempre filtradas por tenant
