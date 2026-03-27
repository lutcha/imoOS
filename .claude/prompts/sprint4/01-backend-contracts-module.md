# Sprint 4 — Backend: Módulo de Contratos

## Pré-requisitos — Ler antes de começar

```
apps/crm/models.py          → UnitReservation (STATUS_CONVERTED, convert_reservation())
apps/inventory/models.py    → Unit (STATUS_CONTRACT, STATUS_AVAILABLE, STATUS_RESERVED)
apps/core/models.py         → TenantAwareModel (herdar daqui)
apps/memberships/models.py  → TenantMembership (para IsTenantAdmin permission)
apps/users/permissions.py   → IsTenantMember, IsTenantAdmin
```

Confirmar que `apps/contracts/` não existe antes de criar:
```bash
ls apps/contracts/ 2>/dev/null && echo "JA EXISTE — ler tudo antes de editar" || echo "NAO EXISTE"
```

## Skills a carregar

```
@.claude/skills/09-module-contracts/contract-lifecycle/SKILL.md
@.claude/skills/09-module-contracts/payment-schedule/SKILL.md
@.claude/skills/02-backend-django/model-audit-history/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
```

## Agents a activar (por esta ordem)

| Agent | Tarefa | Prompt |
|-------|--------|--------|
| `model-architect` | Criar modelos Contract + Payment | Ver Tarefa 1 abaixo |
| `drf-viewset-builder` | Gerar ContractViewSet + PaymentViewSet | Ver Tarefa 2 abaixo |
| `celery-task-specialist` | Task: gerar PDF do contrato | Ver Tarefa 3 abaixo |
| `isolation-test-writer` | Testes de isolamento de contratos | Ver Tarefa 4 abaixo |

---

## Tarefa 1 — Criar `apps/contracts/models.py`

Prompt para `model-architect`:
> "Cria os modelos `Contract` e `Payment` para ImoOS. `Contract` herda de `TenantAwareModel`, tem FK para `UnitReservation`, `Lead`, `Unit`, e `User` (vendedor). Status: DRAFT → ACTIVE → COMPLETED → CANCELLED. `Payment` tem FK para `Contract`, tipo (DEPOSIT/INSTALLMENT/FINAL), valor CVE, data prevista, data efectiva, status (PENDING/PAID/OVERDUE). Ambos com HistoricalRecords. `Contract` tem UniqueConstraint: só um contrato ACTIVE por reserva."

```python
# Estrutura esperada:
class Contract(TenantAwareModel):
    STATUS_DRAFT = 'DRAFT'
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Rascunho'),
        (STATUS_ACTIVE, 'Activo'),
        (STATUS_COMPLETED, 'Concluído'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

    reservation = models.OneToOneField(
        'crm.UnitReservation', on_delete=models.PROTECT, related_name='contract',
        null=True, blank=True,
    )
    unit = models.ForeignKey(
        'inventory.Unit', on_delete=models.PROTECT, related_name='contracts',
    )
    lead = models.ForeignKey(
        'crm.Lead', on_delete=models.PROTECT, related_name='contracts',
    )
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='contracts_as_vendor',
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    contract_number = models.CharField(max_length=50, unique=True)  # ex: ImoOS-2026-0001
    total_price_cve = models.DecimalField(max_digits=14, decimal_places=2)
    signed_at = models.DateTimeField(null=True, blank=True)
    pdf_s3_key = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        constraints = [
            models.UniqueConstraint(
                fields=['reservation'],
                condition=models.Q(status='ACTIVE'),
                name='unique_active_contract_per_reservation',
            )
        ]


class Payment(TenantAwareModel):
    PAYMENT_DEPOSIT = 'DEPOSIT'
    PAYMENT_INSTALLMENT = 'INSTALLMENT'
    PAYMENT_FINAL = 'FINAL'

    TYPE_CHOICES = [
        (PAYMENT_DEPOSIT, 'Sinal'),
        (PAYMENT_INSTALLMENT, 'Prestação'),
        (PAYMENT_FINAL, 'Pagamento Final'),
    ]

    STATUS_PENDING = 'PENDING'
    STATUS_PAID = 'PAID'
    STATUS_OVERDUE = 'OVERDUE'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_PAID, 'Pago'),
        (STATUS_OVERDUE, 'Em Atraso'),
    ]

    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name='payments',
    )
    payment_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    amount_cve = models.DecimalField(max_digits=14, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reference = models.CharField(max_length=100, blank=True)  # referência bancária MBE
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['due_date']
```

---

## Tarefa 2 — `apps/contracts/views.py` + serializers

Prompt para `drf-viewset-builder`:
> "Gera `ContractViewSet` e `PaymentViewSet` para ImoOS. `ContractViewSet`: permission `IsTenantMember` (leitura) e `IsTenantAdmin` (criar/actualizar/cancelar). Action `activate` (DRAFT→ACTIVE, chama `convert_reservation()` do CRM, actualiza `unit.status=CONTRACT`, gera PDF async). Action `cancel` (ACTIVE→CANCELLED, liberta reserva e unidade). `PaymentViewSet`: filtros por `contract`, `status`, `payment_type`. Action `mark_paid` (regista `paid_date=today`, actualiza status). Incluir `ContractSerializer` com `payments` nested (read-only)."

```python
class ContractViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsTenantMember]

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        DRAFT → ACTIVE.
        1. Chama convert_reservation() do CRM (unit.status = CONTRACT)
        2. Gera PDF async via Celery
        3. Avança lead stage para 'won'
        """

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        ACTIVE → CANCELLED.
        Liberta a reserva (CANCELLED) e a unidade (AVAILABLE).
        Lead stage não é revertido automaticamente.
        """
```

---

## Tarefa 3 — Celery task: gerar PDF do contrato

Prompt para `celery-task-specialist`:
> "Adiciona a `apps/contracts/tasks.py` a task `generate_contract_pdf`. Segue o padrão de `crm.generate_proposal_pdf` (tenant_schema string, tenant_context, WeasyPrint, S3 upload). Key S3: `tenants/{slug}/contracts/{contract_id}/{uuid}.pdf`. Após upload, actualiza `contract.pdf_s3_key`. Template: `apps/contracts/templates/contracts/contract.html` com dados do contrato, plano de pagamentos, cláusulas legais (pt-CV placeholder)."

---

## Tarefa 4 — Testes de isolamento

Prompt para `isolation-test-writer`:
> "Escreve `tests/tenant_isolation/test_contract_isolation.py`. Verificar: (1) contrato de tenant_a não visível em tenant_b, (2) activate() numa reserva de outro tenant → 404, (3) pagamento registado no schema correcto, (4) cancel() liberta a unidade no schema correcto."

---

## Tarefa 5 — Registar URLs e apps

**`apps/contracts/urls.py`** — criar:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'contracts', ContractViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [path('', include(router.urls))]
```

**`config/urls.py`** — ler antes de editar, adicionar:
```python
path('api/v1/contracts/', include('apps.contracts.urls')),
```

**`config/settings/base.py`** — adicionar `apps.contracts` a `TENANT_APPS`.

---

## Verificação final

- [ ] `python manage.py check` sem erros
- [ ] `python manage.py migrate_schemas` sem erros
- [ ] `POST /api/v1/contracts/contracts/` com dados válidos → 201
- [ ] `POST /api/v1/contracts/contracts/{id}/activate/` → unit.status = CONTRACT
- [ ] `POST /api/v1/contracts/contracts/{id}/cancel/` → unit.status = AVAILABLE
- [ ] `POST /api/v1/contracts/payments/{id}/mark-paid/` → payment.status = PAID
- [ ] `pytest tests/tenant_isolation/test_contract_isolation.py -v` — todos passing
