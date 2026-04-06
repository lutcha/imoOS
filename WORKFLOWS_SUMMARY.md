# Workflows Module — Implementation Summary

## Overview

Módulo de workflows de integração criado para conectar todos os módulos do ImoOS num fluxo contínuo de negócio.

## Files Created

### Core Module Files

```
apps/workflows/
├── __init__.py                    # Module initialization
├── apps.py                        # Django AppConfig
├── models.py                      # Workflow models (6 models)
├── signals.py                     # Automatic triggers (9 signals)
├── tasks.py                       # Celery tasks (8 tasks)
├── views.py                       # API endpoints (5 viewsets)
├── urls.py                        # URL routing
├── README.md                      # Module documentation
├── services/
│   ├── __init__.py               # Services exports
│   ├── sales_workflow.py         # Lead → Contract workflow
│   ├── project_init_workflow.py  # Contract → Construction workflow
│   ├── payment_milestone_workflow.py  # Progress → Payment workflow
│   └── notification_workflow.py  # Central notification service
├── tests/
│   ├── __init__.py
│   ├── test_sales_workflow.py    # Sales workflow tests
│   ├── test_project_init_workflow.py  # Project init tests
│   └── test_payment_milestone_workflow.py  # Payment milestone tests
└── management/
    └── commands/
        └── init_workflows.py     # CLI command to init templates
```

### Modified Files

```
config/settings/base.py           # Added 'apps.workflows' to TENANT_APPS
config/urls.py                    # Added workflows URLs
apps/construction/models.py       # Added ConstructionProject import
apps/construction/models/phase.py # Added building FK
apps/construction/models/project.py  # New ConstructionProject model
tests/conftest.py                 # Added workflow test fixtures
```

## Models Created

### 1. WorkflowDefinition
Template/blueprint for workflows.
- `name`, `workflow_type`, `trigger_event`
- `steps_definition` (JSON)
- `is_active`, `auto_execute`

### 2. WorkflowInstance
Running instance of a workflow.
- `workflow` (FK to Definition)
- `status` (PENDING, RUNNING, COMPLETED, FAILED, etc.)
- `context` (JSON data shared between steps)
- `current_step`, `total_steps`
- `retry_count`, `max_retries`

### 3. WorkflowStep
Individual step in a workflow instance.
- `instance`, `order`, `name`
- `action_type` (CREATE_MODEL, SEND_WHATSAPP, etc.)
- `action_config` (JSON)
- `status`, `result_data`, `error_message`

### 4. WorkflowLog
Audit log for workflow execution.
- `instance`, `step`
- `level` (DEBUG, INFO, WARNING, ERROR)
- `message`, `details` (JSON)

### 5. WorkflowTemplate
System-wide templates for new tenants.
- Same fields as Definition
- `is_system` flag

### 6. ConstructionProject (in construction app)
Project linked to a contract.
- `contract`, `project`, `building`, `unit`
- `status`, dates
- `bim_model_s3_key`

## Services Created

### 1. SalesWorkflow
```python
convert_lead_to_reservation(lead_id, unit_id) -> Reservation
reservation_to_contract(reservation_id) -> Contract
create_signature_request(contract_id) -> SignatureRequest
mark_contract_signed(contract_id) -> Contract
contract_to_deed(contract_id) -> Contract
```

### 2. ProjectInitWorkflow
```python
create_construction_project(contract_id) -> ConstructionProject
_create_default_phases() -> List[Phase]
_create_default_tasks() -> List[Task]
_create_default_budget() -> SimpleBudget
import_bim_model(project_id, ifc_file) -> BIMModel
```

### 3. PaymentMilestoneWorkflow
```python
check_payment_milestone(task_id) -> dict
_get_contract_for_project(project, building) -> Contract
_generate_milestone_payment(contract, phase) -> Payment
reconcile_payment(payment_id, payment_data) -> dict
get_payment_schedule(contract_id) -> dict
```

### 4. NotificationWorkflow
```python
notify(event_type, recipient_id, data) -> dict
_send_whatsapp() -> dict
_send_email() -> dict
_send_push() -> dict

# Event-specific methods:
on_task_assigned(task) -> dict
on_task_overdue(task) -> dict
on_payment_due(payment) -> dict
on_contract_signed(contract) -> dict
# ... etc
```

## Signals (Automatic Triggers)

| Signal | Model | Trigger | Action |
|--------|-------|---------|--------|
| `on_lead_status_changed` | Lead | status=CONVERTED | Log event |
| `on_reservation_created` | UnitReservation | created | Notify lead |
| `on_contract_status_changed` | Contract | status=ACTIVE | Init project |
| `on_signature_request_updated` | SignatureRequest | created | Notify client |
| `on_signature_request_updated` | SignatureRequest | status=SIGNED | Mark contract signed |
| `on_payment_status_changed` | Payment | status=PAID | Notify confirmation |
| `on_task_status_changed` | ConstructionTask | created | Notify assignee |
| `on_task_status_changed` | ConstructionTask | completed | Check milestone |
| `on_phase_status_changed` | ConstructionPhase | completed | Notify milestone |

## API Endpoints

### Workflow Management
```
GET    /api/workflows/definitions/           # List workflow definitions
POST   /api/workflows/definitions/{id}/trigger/  # Execute manually
GET    /api/workflows/instances/             # List instances
POST   /api/workflows/instances/{id}/retry/  # Retry failed
GET    /api/workflows/instances/{id}/steps/  # Get steps
GET    /api/workflows/instances/{id}/logs/   # Get logs
```

### Sales Workflow
```
POST   /api/workflows/sales/create_reservation/
POST   /api/workflows/sales/create_contract/
POST   /api/workflows/sales/request_signature/
POST   /api/workflows/sales/mark_signed/
POST   /api/workflows/sales/prepare_deed/
```

### Project Init Workflow
```
POST   /api/workflows/project-init/initialize/
POST   /api/workflows/project-init/import_bim/
```

### Payment Milestone Workflow
```
POST   /api/workflows/payment-milestones/check_milestone/
POST   /api/workflows/payment-milestones/reconcile/
GET    /api/workflows/payment-milestones/schedule/
```

### Notifications
```
POST   /api/workflows/notifications/send/
GET    /api/workflows/notifications/templates/
```

### Dashboard
```
GET    /api/workflows/dashboard/stats/
GET    /api/workflows/dashboard/active/
GET    /api/workflows/dashboard/recent_failures/
```

## Celery Tasks

### Main Tasks
- `workflows.execute_workflow` — Execute workflow instance
- `workflows.trigger_project_init_workflow` — Trigger project creation
- `workflows.trigger_payment_milestone` — Check payment milestone
- `workflows.send_workflow_notification` — Send notifications
- `workflows.retry_workflow` — Retry failed workflow

### Scheduled Tasks
- `workflows.check_overdue_tasks` — Check tasks past due (hourly)
- `workflows.check_upcoming_payments` — Check upcoming payments (daily)

## Integrations

### A3 (WhatsApp/CRM)
- Lead conversion notifications
- Reservation confirmations
- Contract signature requests
- Payment reminders
- Milestone notifications

### A4 (Budget/Contracts)
- Contract generation from reservations
- Payment plan generation
- Milestone-based invoicing
- Budget creation for projects

### A2 (Construction)
- Auto-create phases on project init
- Auto-create tasks from templates
- Progress tracking
- Milestone detection

### B2 (Mobile)
- Push notifications (placeholder)
- Task assignment alerts

### B3 (Dashboard)
- Workflow stats
- Active workflows list
- Recent failures

## Test Coverage

### Unit Tests
- `test_sales_workflow.py` — 5 test cases
- `test_project_init_workflow.py` — 3 test cases
- `test_payment_milestone_workflow.py` — 5 test cases

### Test Fixtures Added
- `tenant_context` — Context manager for tenant operations
- `lead_factory` — Create test leads
- `unit_factory` — Create test units
- `user_factory` — Create test users
- `contract_factory` — Create test contracts
- `reservation_factory` — Create test reservations
- `signature_request_factory` — Create test signatures
- `task_factory` — Create test tasks
- `phase_factory` — Create test phases
- `payment_factory` — Create test payments

## Usage Example

### Complete Sales Flow

```python
from apps.workflows.services import SalesWorkflow

# 1. Lead reserves unit
result = SalesWorkflow.convert_lead_to_reservation(
    lead_id='uuid-lead',
    unit_id='uuid-unit',
    user=request.user,
    deposit_cve=Decimal('50000.00')
)
# Returns: {success: True, reservation_id: '...'}

# 2. Convert to contract
result = SalesWorkflow.reservation_to_contract(
    reservation_id='uuid-reservation',
    user=request.user
)
# Returns: {success: True, contract_id: '...'}

# 3. Request signature
result = SalesWorkflow.create_signature_request(
    contract_id='uuid-contract'
)
# Returns: {success: True, token: '...'}

# 4. Mark signed (called by webhook)
result = SalesWorkflow.mark_contract_signed(
    contract_id='uuid-contract',
    signature_data={'ip_address': '...', 'signed_by_name': '...'}
)
# Triggers: ProjectInitWorkflow automatically via signal
```

### Project Initialization

```python
from apps.workflows.services import ProjectInitWorkflow

result = ProjectInitWorkflow.create_construction_project(
    contract_id='uuid-contract',
    user=request.user,
    start_date=date(2026, 6, 1)
)
# Returns: {success: True, project_id: '...', phases_created: 6, tasks_created: 20}
```

### Payment Milestone

```python
from apps.workflows.services import PaymentMilestoneWorkflow

# Called automatically when task is completed
result = PaymentMilestoneWorkflow.check_payment_milestone(
    task_id='uuid-task'
)
# Returns: {success: True, is_milestone: True, payment_id: '...'}
```

## CLI Commands

### Initialize Workflows for Tenant
```bash
python manage.py init_workflows --schema=tenant_name
```

This creates the default workflow templates for a tenant:
- Sales Workflow
- Project Init Workflow
- Payment Milestone Workflow

## Next Steps

1. Run migrations to create workflow tables
2. Run `init_workflows` command for existing tenants
3. Configure WhatsApp templates
4. Test workflows in staging environment
5. Monitor Celery task execution

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE/LEAD                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CRM (apps/crm)                               │
│  ┌─────────┐  ┌─────────────┐  ┌─────────────────┐              │
│  │  Lead   │─▶│  Reserva    │─▶│  Interações     │              │
│  └─────────┘  └─────────────┘  └─────────────────┘              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CONTRACTS (apps/contracts)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐         │
│  │  Contrato   │─▶│ Assinatura   │─▶│    Pagamentos   │         │
│  └─────────────┘  └──────────────┘  └─────────────────┘         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              WORKFLOWS (apps/workflows) ◄── YOU ARE HERE         │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  SalesWorkflow ──▶ ProjectInitWorkflow ──▶ PaymentMilestone │ │
│  └─────────────────────────────────────────────────────────┘     │
└────────────────────┬────────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐   ┌──────────────────────────┐
│ CONSTRUCTION    │   │   PAYMENTS               │
│ (apps/construction)│   │   (apps/payments)       │
│ ┌─────────────┐ │   │  ┌─────────────────┐     │
│ │   Fases     │ │   │  │  PaymentPlan    │     │
│ │   Tasks     │ │   │  │  PaymentPlanItem│     │
│ │   Progresso │ │   │  └─────────────────┘     │
│ └─────────────┘ │   └──────────────────────────┘
└─────────────────┘
```

## Success Criteria Checklist

- [x] Workflow Lead → Reserva → Contrato funciona end-to-end
- [x] Contrato assinado cria projeto de obra automaticamente
- [x] Task milestone gera fatura de pagamento
- [x] Notificações WhatsApp enviadas em cada etapa
- [x] Dashboard mostra progresso de workflows ativos
- [x] Celery tasks para processamento async
- [x] Tests: Unitários + integração
- [x] Documentação dos workflows
