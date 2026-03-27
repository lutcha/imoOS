# Sprint 5 — Backend: Planos de Pagamento (`apps/payments`)

## Contexto

`apps/payments/` existe como directório vazio. O módulo de pagamentos complementa
`apps/contracts/` — enquanto `Contract` tem uma lista plana de `Payment`, este
módulo adiciona planos de pagamento estruturados (sinal + prestações + final),
geração de referências MBE (Multibanco), e rastreio de estado por contrato.

## Pré-requisitos — Ler antes de começar

```
apps/contracts/models.py        → Contract, Payment (já existem)
apps/contracts/serializers.py   → PaymentSerializer (já existe)
apps/contracts/views.py         → PaymentViewSet.mark_paid (já existe)
apps/core/models.py             → TenantAwareModel
config/settings/base.py         → TENANT_APPS
```

```bash
# Verificar o que já existe em apps/payments
ls apps/payments/

# Verificar se Payment já é suficiente ou precisamos de modelos novos
grep "class Payment\|class PaymentPlan" apps/contracts/models.py apps/payments/ 2>/dev/null
```

## Skills a carregar

```
@.claude/skills/12-module-payments/payment-plan-generator/SKILL.md
@.claude/skills/12-module-payments/installment-scheduler/SKILL.md
@.claude/skills/12-module-payments/mbe-reference/SKILL.md
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `model-architect` | PaymentPlan + PaymentPlanItem models |
| `drf-viewset-builder` | PaymentPlanViewSet com generate action |
| `celery-task-specialist` | Task: enviar lembretes de pagamento |
| `isolation-test-writer` | Testes de isolamento de pagamentos |

---

## Tarefa 1 — Modelos (`apps/payments/models.py`)

Prompt para `model-architect`:
> "Cria `PaymentPlan` e `PaymentPlanItem` para ImoOS em `apps/payments/`. `PaymentPlan`: OneToOne com `Contract`, tipo (STANDARD/CUSTOM), total_cve, gerado_em. `PaymentPlanItem`: FK para `PaymentPlan`, tipo (DEPOSIT/INSTALLMENT/FINAL), percentagem (Decimal), valor_cve, data_prevista, FK para `Payment` (apps.contracts) quando liquidado, referência MBE (CharField). Ambos com TenantAwareModel + HistoricalRecords."

```python
class PaymentPlan(TenantAwareModel):
    TYPE_STANDARD = 'STANDARD'   # 10% sinal + 80% prestações + 10% final
    TYPE_CUSTOM   = 'CUSTOM'     # plano personalizado

    contract = models.OneToOneField(
        'contracts.Contract', on_delete=models.CASCADE, related_name='payment_plan',
    )
    plan_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_STANDARD)
    total_cve = models.DecimalField(max_digits=14, decimal_places=2)
    notes = models.TextField(blank=True)
    history = HistoricalRecords()

    def generate_standard(self, installments: int = 8) -> None:
        """
        Gera itens de plano padrão: 10% sinal, (80/N)% × N prestações mensais, 10% final.
        Idempotente — apaga itens existentes antes de gerar.
        """


class PaymentPlanItem(TenantAwareModel):
    TYPE_DEPOSIT     = 'DEPOSIT'
    TYPE_INSTALLMENT = 'INSTALLMENT'
    TYPE_FINAL       = 'FINAL'

    plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    amount_cve = models.DecimalField(max_digits=14, decimal_places=2)
    due_date = models.DateField()
    payment = models.OneToOneField(
        'contracts.Payment', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='plan_item',
    )
    mbe_reference = models.CharField(max_length=25, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    history = HistoricalRecords()

    class Meta:
        ordering = ['order', 'due_date']
```

---

## Tarefa 2 — Gerador de referência MBE

```python
# apps/payments/mbe.py
# Referência Multibanco Cabo Verde: ENTIDADE (5 dígitos) + REFERÊNCIA (9 dígitos) + VALOR

import hashlib

def generate_mbe_reference(contract_id: str, item_order: int, amount_cve: int) -> str:
    """
    Gera referência MBE determinista: mesmo input → mesma referência.
    Formato: {9 dígitos derivados do contract_id + order}

    Em produção: integrar com gateway MBE real (ex: ifthenpay, euPago).
    """
    seed = f"{contract_id}:{item_order}:{amount_cve}"
    digest = hashlib.sha256(seed.encode()).hexdigest()
    # 9 dígitos numéricos
    return str(int(digest[:8], 16) % 10**9).zfill(9)
```

---

## Tarefa 3 — ViewSet (`apps/payments/views.py`)

Prompt para `drf-viewset-builder`:
> "Gera `PaymentPlanViewSet` para ImoOS. Read: IsTenantMember. Write: IsTenantAdmin. Action `generate` (POST): recebe `installments` (default 8), chama `plan.generate_standard()`, gera referências MBE para cada item. Action `regenerate` (POST): apaga itens e gera de novo. Serializer inclui `items` nested com status de cada pagamento. Filtro por `contract`."

---

## Tarefa 4 — Celery task: lembretes de pagamento

Prompt para `celery-task-specialist`:
> "Cria `apps/payments/tasks.py` com `send_payment_reminders`. Recebe `tenant_schema`. Dentro de `tenant_context`: busca PaymentPlanItems com `due_date` nos próximos 7 dias e `payment__isnull=True` (não pago). Para cada item: envia WhatsApp ao lead do contrato (se WHATSAPP_ENABLED). Cache key `{tenant}:payment_reminder:{item_id}:{due_date}` para idempotência. Retry ×3 exponencial."

---

## Tarefa 5 — Registar no projecto

`apps/payments/urls.py`:
```python
router.register(r'plans', PaymentPlanViewSet, basename='payment-plan')
urlpatterns = [path('', include(router.urls))]
```

`config/urls.py`:
```python
path('api/v1/payments/', include('apps.payments.urls')),
```

`config/settings/base.py` → `TENANT_APPS`: adicionar `'apps.payments'`

---

## Tarefa 6 — Testes de isolamento

Prompt para `isolation-test-writer`:
> "Escreve `tests/tenant_isolation/test_payment_isolation.py`. Verificar: (1) plano de pagamento de tenant_a não visível em tenant_b, (2) generate action num contrato de outro tenant → 404, (3) referência MBE isolada por schema."

---

## Verificação final

- [ ] `python manage.py migrate_schemas` sem erros
- [ ] `POST /api/v1/payments/plans/` + `POST /api/v1/payments/plans/{id}/generate/` → itens gerados
- [ ] Referências MBE geradas para cada item
- [ ] `pytest tests/tenant_isolation/test_payment_isolation.py -v`
