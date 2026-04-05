# Construction App - ImoOS

Sistema de gestão de obra com dois modos de operação: **Simple Mode** (padrão) e **Advanced Mode** (CPM/EVM).

## Arquitetura

```
apps/construction/
├── models/
│   ├── __init__.py          # Exports
│   ├── phase.py             # ConstructionPhase (WBS Level 1)
│   ├── task.py              # ConstructionTask (Simple + Advanced)
│   ├── progress.py          # TaskPhoto, TaskProgressLog
│   ├── cpm.py               # TaskDependency, CPMSnapshot
│   └── evm.py               # EVMSnapshot
├── services/
│   ├── __init__.py
│   ├── cpm_calculator.py    # Algoritmo CPM
│   ├── evm_calculator.py    # Cálculos EVM
│   └── progress_updater.py  # Atualização de progresso
├── views.py                 # API ViewSets
├── urls.py                  # Rotas API
├── serializers.py           # Serializers DRF
├── admin.py                 # Admin Django
├── signals.py               # Notificações WhatsApp
├── tasks.py                 # Tarefas Celery
├── permissions.py           # Permissões custom
└── tests/                   # Testes
```

## Modos de Operação

### Simple Mode (Padrão)

Para gestão direta de tarefas sem complexidade:

- **Tasks**: Status simples (Pendente, Em Andamento, Concluído)
- **Progresso**: Slider 0-100%
- **Datas**: Due date apenas
- **Custo**: Estimated vs Actual

```python
task = ConstructionTask.objects.create(
    wbs_code='1.1',
    name='Escavação',
    status='PENDING',
    due_date=date(2026, 6, 30),
    estimated_cost=Decimal('50000.00'),
)
```

### Advanced Mode (CPM/EVM)

Para projetos que precisam de análise de caminho crítico e valor ganho:

```python
task = ConstructionTask.objects.create(
    wbs_code='1.1',
    name='Escavação',
    advanced_mode='ON',
    duration_days=10,
)

# Criar dependências
TaskDependency.objects.create(
    from_task=task_a,
    to_task=task_b,
    dependency_type='FS',  # Finish-to-Start
    lag_days=2
)

# Recalcular CPM
from apps.construction.services import CPMCalculator
calculator = CPMCalculator(project_id)
stats = calculator.recalculate_project()
```

## API Endpoints

### Fases
```
GET    /api/v1/construction/phases/?project={id}
POST   /api/v1/construction/phases/
PATCH  /api/v1/construction/phases/{id}/
```

### Tasks
```
GET    /api/v1/construction/tasks/?project={id}&status={}&assigned_to={id}
POST   /api/v1/construction/tasks/
PATCH  /api/v1/construction/tasks/{id}/
POST   /api/v1/construction/tasks/{id}/update_progress/
POST   /api/v1/construction/tasks/{id}/start/
POST   /api/v1/construction/tasks/{id}/complete/
POST   /api/v1/construction/tasks/{id}/upload_photo/
GET    /api/v1/construction/tasks/{id}/progress_timeline/
POST   /api/v1/construction/tasks/{id}/enable_advanced_mode/

# Mobile (otimizado)
GET    /api/v1/construction/tasks/mobile_list/?assigned_to={id}
```

### CPM (Advanced)
```
GET    /api/v1/construction/cpm/?project={id}
POST   /api/v1/construction/cpm/recalculate/
GET    /api/v1/construction/cpm/gantt/?project={id}
GET    /api/v1/construction/cpm/critical_path/?project={id}
```

### EVM (Advanced)
```
GET    /api/v1/construction/evm/?project={id}&date={YYYY-MM-DD}
POST   /api/v1/construction/evm/calculate/
GET    /api/v1/construction/evm/trend/?project={id}&days={30}
GET    /api/v1/construction/evm/forecast/?project={id}
```

### Dashboard
```
GET    /api/v1/construction/dashboard/?project={id}
```

## Integrações

### WhatsApp (A3)

Notificações automáticas via signals:

- **Atribuição**: Quando task é criada com `assigned_to`
- **Reatribuição**: Quando task muda de responsável
- **Atraso**: Quando task passa do `due_date`
- **Lembrete diário**: Tasks para hoje (8h)

### Budget (A4)

Tasks têm campos de custo:
- `estimated_cost`: Custo estimado (orçamento)
- `actual_cost`: Custo real

EVM usa esses valores para calcular:
- PV (Planned Value)
- EV (Earned Value)
- AC (Actual Cost)

## Cálculos CPM

### Forward Pass
```
ES (Early Start) = max(EF of predecessors) + lag
EF (Early Finish) = ES + duration
```

### Backward Pass
```
LF (Late Finish) = min(LS of successors) - lag
LS (Late Start) = LF - duration
```

### Float
```
Total Float = LS - ES = LF - EF
Free Float = min(ES of successors) - EF
```

### Caminho Crítico
Tasks com `total_float = 0` estão no caminho crítico.

## Cálculos EVM

### Básicos
```
PV = Σ(budget of tasks planned to be done)
EV = Σ(budget × % complete)
AC = Σ(actual cost)
```

### Índices
```
SPI = EV / PV  (>1 = adiantado, <1 = atrasado)
CPI = EV / AC  (>1 = abaixo orçamento, <1 = acima)
```

### Previsões
```
EAC = BAC / CPI
ETC = EAC - AC
VAC = BAC - EAC
TCPI = (BAC - EV) / (BAC - AC)
```

## Tarefas Celery

Configurar em Django Admin > Periodic Tasks:

```python
# 8h diariamente
send_daily_task_reminders

# 9h diariamente  
check_overdue_tasks_task

# 18h diariamente (fim do expediente)
generate_all_evm_snapshots
```

## Testes

```bash
# Unitários
pytest apps/construction/tests/test_models.py -v
pytest apps/construction/tests/test_services.py -v

# Tenant Isolation (MANDATÓRIO)
pytest apps/construction/tests/test_tenant_isolation.py -v
```

## Regras de Negócio

1. **Progresso 100% = Status COMPLETED**: Automático via `save()`
2. **WBS único por projeto**: Constraint `unique_together=['project', 'wbs_code']`
3. **CPM recalcula automaticamente**: Ao criar/alterar dependências
4. **Fases recalculam progresso**: Baseado na média das tasks
5. **Notificações não quebram**: Signals capturam exceções

## Migrações

```bash
python manage.py makemigrations construction
python manage.py migrate_schemas
```

## Permissões

- `IsTenantMember`: Acesso básico
- `IsEngineerOrAdmin`: Criar/editar tasks, dependências

## Futuro (Roadmap)

- [ ] Integração BIM (IFC)
- [ ] ML para estimar progresso via fotos
- [ ] Notificações push (mobile)
- [ ] Offline sync (mobile)
