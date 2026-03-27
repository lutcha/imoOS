# Sprint 2 — Backend: Celery Tasks (CSV Import + WhatsApp)

## Pré-requisito

- `config/celery.py` existe ✓
- `config/__init__.py` importa celery_app ✓
- `apps/inventory/models.py` — Unit, UnitType existem ✓
- `apps/crm/models.py` — Lead existe ✓
- `REDIS_URL` definido em `.env`

## Estado actual das tasks Celery

Nenhuma task existe ainda. Este prompt cria as primeiras duas tasks de produção.

## Skills a carregar

```
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
@.claude/skills/03-async-celery/tenant-task-wrapper/SKILL.md
@.claude/skills/03-async-celery/retry-exponential-backoff/SKILL.md
@.claude/skills/03-async-celery/task-idempotency/SKILL.md
@.claude/skills/03-async-celery/async-email-whatsapp/SKILL.md
@.claude/skills/07-module-inventory/unit-bulk-import-csv/SKILL.md
@.claude/skills/01-multi-tenant/tenant-context/SKILL.md
```

## Agents a activar

| Agent | Para que tarefa |
|-------|----------------|
| `celery-task-specialist` | Criar ambas as tasks com padrão correcto de tenant_context e retry |
| `tenant-expert` | Auditar que as tasks não têm cross-tenant leaks (passar tenant_id, não objecto ORM) |
| `isolation-test-writer` | Escrever testes que confirmam que a task executa no schema correcto |

> **Regra crítica (CLAUDE.md):** Tasks Celery recebem `tenant_id` (string/UUID), nunca objectos ORM.
> Dentro da task, fazer `Client.objects.get(id=tenant_id)` e envolver em `tenant_context()`.

---

## Task 1 — Bulk Import CSV de Unidades

### `apps/inventory/tasks.py` — criar

```python
"""
Task: importar unidades a partir de CSV.
Executa no schema do tenant — cada linha cria ou actualiza uma Unit.

Padrão obrigatório (CLAUDE.md):
- tenant_id passado como argumento (nunca o objecto)
- tenant_context() envolve TODA a lógica de negócio
- idempotência: usar get_or_create com código como chave
- retry com backoff exponencial
"""
import csv, io, logging
from celery import shared_task
from django_tenants.utils import tenant_context
from apps.tenants.models import Client

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='inventory.import_units_csv',
)
def import_units_from_csv(self, tenant_id: str, csv_content: str, uploaded_by_id: str):
    """
    Importa unidades de um CSV.
    Args:
        tenant_id: UUID do Client (nunca o objecto)
        csv_content: conteúdo do CSV como string
        uploaded_by_id: UUID do User que disparou o import
    """
    try:
        tenant = Client.objects.get(id=tenant_id)
    except Client.DoesNotExist:
        logger.error(f"Tenant {tenant_id} não encontrado — task abortada")
        return {'status': 'error', 'detail': 'Tenant não encontrado'}

    results = {'created': 0, 'updated': 0, 'errors': []}

    with tenant_context(tenant):
        from apps.inventory.models import Unit, UnitType
        from apps.projects.models import Floor

        reader = csv.DictReader(io.StringIO(csv_content))

        for row_num, row in enumerate(reader, start=2):
            try:
                # Validação mínima
                required = ['code', 'floor_id', 'unit_type_code', 'area_bruta']
                missing = [f for f in required if not row.get(f)]
                if missing:
                    results['errors'].append(f"Linha {row_num}: campos em falta: {missing}")
                    continue

                floor = Floor.objects.get(id=row['floor_id'])
                unit_type = UnitType.objects.get(code=row['unit_type_code'])

                unit, created = Unit.objects.update_or_create(
                    floor=floor,
                    code=row['code'],
                    defaults={
                        'unit_type': unit_type,
                        'area_bruta': row['area_bruta'],
                        'area_util': row.get('area_util') or None,
                        'orientation': row.get('orientation', ''),
                        'floor_number': row.get('floor_number', 0),
                        'status': row.get('status', 'AVAILABLE'),
                    }
                )

                if created:
                    results['created'] += 1
                else:
                    results['updated'] += 1

            except Exception as e:
                results['errors'].append(f"Linha {row_num}: {str(e)}")
                continue

    logger.info(
        f"[{tenant.schema_name}] CSV import: {results['created']} criadas, "
        f"{results['updated']} actualizadas, {len(results['errors'])} erros"
    )
    return results
```

### Endpoint para disparar a task — adicionar a `apps/inventory/views.py`

```python
@action(detail=False, methods=['post'], url_path='import-csv')
def import_csv(self, request):
    """Upload CSV → Celery task assíncrona → retorna task_id."""
    from .tasks import import_units_from_csv

    csv_file = request.FILES.get('file')
    if not csv_file:
        return Response({'detail': 'Ficheiro CSV obrigatório.'}, status=400)

    if not csv_file.name.endswith('.csv'):
        return Response({'detail': 'Formato inválido. Apenas .csv aceite.'}, status=400)

    csv_content = csv_file.read().decode('utf-8-sig')  # utf-8-sig para BOM de Excel

    task = import_units_from_csv.delay(
        tenant_id=str(request.tenant.id),
        csv_content=csv_content,
        uploaded_by_id=str(request.user.id),
    )

    return Response({'task_id': task.id, 'status': 'queued'}, status=202)
```

**CSV template esperado:**
```csv
code,floor_id,unit_type_code,area_bruta,area_util,orientation,floor_number,status
A-P1-01,{uuid},T2,75.5,68.0,Mar,1,AVAILABLE
A-P1-02,{uuid},T3,95.0,85.0,Norte,1,AVAILABLE
```

---

## Task 2 — Notificação WhatsApp após captura de lead

### `apps/crm/tasks.py` — criar

```python
"""
Task: notificar vendedor via WhatsApp quando novo lead é capturado.
Dispara após LeadCaptureView.perform_create().
"""
import logging
import requests
from celery import shared_task
from django_tenants.utils import tenant_context
from apps.tenants.models import Client

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=5,
    name='crm.notify_whatsapp_new_lead',
)
def notify_whatsapp_new_lead(self, tenant_id: str, lead_id: str):
    """
    Envia mensagem WhatsApp ao vendedor assignado (ou admin) sobre novo lead.
    """
    try:
        tenant = Client.objects.get(id=tenant_id)
    except Client.DoesNotExist:
        return

    with tenant_context(tenant):
        from apps.crm.models import Lead

        try:
            lead = Lead.objects.get(id=lead_id)
        except Lead.DoesNotExist:
            return

        # Obter configuração do WhatsApp para este tenant
        settings_obj = getattr(tenant, 'settings', None)
        if not settings_obj or not settings_obj.whatsapp_phone_id:
            logger.info(f"[{tenant.schema_name}] WhatsApp não configurado — skip")
            return

        # Destinatário: vendedor assignado ou primeiro admin do tenant
        recipient = lead.assigned_to
        if not recipient or not recipient.phone:
            from apps.users.models import User
            recipient = User.objects.filter(role='admin').first()

        if not recipient or not recipient.phone:
            logger.warning(f"[{tenant.schema_name}] Sem destinatário WhatsApp para lead {lead_id}")
            return

        message = (
            f"🏠 *Novo Lead — ImoOS*\n\n"
            f"Nome: {lead.first_name} {lead.last_name}\n"
            f"Email: {lead.email}\n"
            f"Fonte: {lead.get_source_display()}\n"
            f"Orçamento: {lead.budget:,.0f} CVE" if lead.budget else f"Orçamento: Não indicado"
        )

        _send_whatsapp_message(
            phone_id=settings_obj.whatsapp_phone_id,
            to=recipient.phone,
            message=message,
        )

def _send_whatsapp_message(phone_id: str, to: str, message: str):
    """Seguir skill async-email-whatsapp para implementação completa."""
    from django.conf import settings as django_settings

    token = django_settings.WHATSAPP_API_TOKEN
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"

    resp = requests.post(url, headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }, json={
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }, timeout=10)

    resp.raise_for_status()
    return resp.json()
```

### Ligar a task ao `LeadCaptureView`

Em `apps/crm/views_public.py`, actualizar `perform_create`:

```python
def perform_create(self, serializer):
    lead = serializer.save()

    # Disparar notificação assíncrona — não bloquear o request
    from .tasks import notify_whatsapp_new_lead
    notify_whatsapp_new_lead.delay(
        tenant_id=str(self.request.tenant.id),
        lead_id=str(lead.id),
    )
```

---

## Testes das tasks

### `tests/test_celery_tasks.py` — criar

```python
"""
Testes para as tasks Celery.
Usam CELERY_TASK_ALWAYS_EAGER=True (execução síncrona no teste).
"""
import pytest
from django_tenants.utils import tenant_context

@pytest.mark.django_db
class TestImportUnitsCsvTask:

    def test_import_csv_cria_unidades_no_schema_correcto(self, tenant_a):
        """Task deve criar unidades apenas no schema de tenant_a."""
        from apps.inventory.tasks import import_units_from_csv
        from apps.inventory.models import Unit

        # ... setup floor + unit_type em tenant_a
        # ... chamar import_units_from_csv.apply(args=[str(tenant_a.id), csv, user_id])
        # ... assert Unit.objects.count() == n dentro de tenant_context(tenant_a)

    def test_import_csv_nao_afecta_outros_tenants(self, tenant_a, tenant_b):
        """Importação em tenant_a não cria unidades em tenant_b."""
        # Seguir skill isolation-test-template
        pass
```

Invocar agent: `isolation-test-writer` com prompt:
> "Escreve testes de isolamento para `import_units_from_csv` e `notify_whatsapp_new_lead`.
> Confirma que cada task opera exclusivamente no schema do tenant passado como argumento."

## Verificação final

- [ ] `POST /api/v1/inventory/units/import-csv/` com CSV válido retorna `{ task_id, status: "queued" }`
- [ ] Worker Celery processa a task sem erro (`make logs` → celery worker logs)
- [ ] Unidades criadas pelo CSV aparecem em `GET /api/v1/inventory/units/`
- [ ] Task de WhatsApp dispara após `POST /api/v1/crm/lead-capture/`
- [ ] Task falha graciosamente quando WhatsApp não está configurado (sem exception)
- [ ] `pytest tests/test_celery_tasks.py` — 100% passing
