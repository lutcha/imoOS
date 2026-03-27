# Sprint 8 — Activar Integração imo.cv (Marketplace)

## Contexto

O módulo `apps/marketplace/` foi implementado no Sprint 6 (Prompt 00).
Este prompt activa a integração em staging com o imo.cv real:
1. Configurar credenciais da API imo.cv por tenant
2. Testar publicação de unidade de staging → imo.cv
3. Testar webhook de recepção de lead do imo.cv → ImoOS CRM
4. Activar sync automático diário

O imo.cv já está a correr localmente (Docker: `imocv_frontend:3000`, `imocv_backend:8000`).

## Pré-requisitos — Ler antes de começar

```
apps/marketplace/models.py      → MarketplaceListing, ImoCvWebhookLog
apps/marketplace/tasks.py       → sync_unit_listing, process_imocv_webhook
apps/marketplace/views.py       → MarketplaceListingViewSet
apps/crm/models.py              → Lead (source='IMOCV')
apps/tenants/models.py          → TenantSettings.imocv_api_key
config/urls_public.py           → webhook endpoint
```

```bash
# Verificar o que já está implementado
ls apps/marketplace/
python manage.py show_urls 2>/dev/null | grep marketplace
grep "imocv\|marketplace" config/urls.py config/urls_public.py
```

## Skills a carregar

```
@.claude/skills/09-integrations/imocv-marketplace/SKILL.md
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
@.claude/skills/16-security-compliance/webhook-verification/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `celery-task-specialist` | Activar + testar sync tasks com imo.cv local |
| `drf-viewset-builder` | Webhook endpoint verificação + frontend /marketplace |
| `schema-isolation-auditor` | Auditar que listings de tenant A não aparecem em tenant B |

---

## Tarefa 1 — Verificar modelo e migrations

```bash
# Confirmar que MarketplaceListing existe
python manage.py showmigrations marketplace 2>/dev/null || echo "App não registada"
grep "marketplace" config/settings/base.py

# Se não existir, adicionar a TENANT_APPS e criar migrations
python manage.py makemigrations marketplace
python manage.py migrate_schemas
```

---

## Tarefa 2 — TenantSettings: imocv_api_key

**Ler `apps/tenants/models.py` antes de editar.**

Verificar se `TenantSettings` tem os campos de imo.cv:
```python
imocv_api_key = models.CharField(max_length=200, blank=True,
    help_text="API key da conta imo.cv deste tenant")
imocv_enabled = models.BooleanField(default=False,
    help_text="Activar integração com imo.cv")
imocv_auto_publish = models.BooleanField(default=False,
    help_text="Publicar unidades AVAILABLE automaticamente")
```

Se não existirem, adicionar + migration:
```bash
python manage.py makemigrations tenants --name=add_imocv_settings
python manage.py migrate_schemas
```

---

## Tarefa 3 — Configurar tenant demo com credenciais imo.cv

```python
# No shell Django (schema demo_promotora):
# python manage.py shell

from django_tenants.utils import tenant_context, get_tenant_model
Client = get_tenant_model()
tenant = Client.objects.get(schema_name='demo_promotora')

from apps.tenants.models import TenantSettings
with tenant_context(tenant):
    settings = TenantSettings.objects.get(tenant=tenant)
    settings.imocv_api_key = 'LOCAL_DEV_KEY'  # chave de desenvolvimento local
    settings.imocv_enabled = True
    settings.imocv_auto_publish = True
    settings.save()
    print("imo.cv activado para demo_promotora")
```

---

## Tarefa 4 — Testar publicação de unidade

```python
# Testar ImoCvClient directamente
from django_tenants.utils import tenant_context, get_tenant_model
from apps.marketplace.tasks import sync_unit_listing
from apps.inventory.models import Unit

Client = get_tenant_model()
tenant = Client.objects.get(schema_name='demo_promotora')

with tenant_context(tenant):
    unit = Unit.objects.filter(status='AVAILABLE').first()
    print(f"Sincronizar unidade: {unit.code}")

# Enfileirar task de sync
sync_unit_listing.delay(
    tenant_schema='demo_promotora',
    unit_id=str(unit.id),
)
```

---

## Tarefa 5 — Webhook de leads do imo.cv → ImoOS CRM

O webhook recebe leads que contactaram via imo.cv e cria-os no CRM:

```python
# apps/marketplace/views.py — endpoint público
# POST /api/public/webhooks/imocv/lead/
# Payload imo.cv:
# {
#   "event": "lead.created",
#   "listing_id": "abc123",
#   "lead": {
#     "name": "João Silva",
#     "email": "joao@gmail.com",
#     "phone": "+238 991 0000",
#     "message": "Interesse na unidade T2"
#   },
#   "signature": "sha256=..."
# }

# 1. Verificar assinatura HMAC-SHA256
# 2. Encontrar MarketplaceListing por imocv_listing_id
# 3. Resolver tenant (via listing → unit → schema)
# 4. Criar Lead(source='IMOCV') no schema correcto
# 5. Registar ImoCvWebhookLog
# 6. Retornar 200 (sempre — não reenviar em erro 4xx)
```

---

## Tarefa 6 — Frontend: /marketplace

Verificar se `frontend/src/app/marketplace/page.tsx` existe.
Se não existir, criar:

```typescript
// Página de gestão do marketplace
// Tabs: Listagens Activas | Sincronização | Configuração

// Tab Listagens:
//   - Tabela: Unidade | Código imo.cv | Estado | Último sync | Erro
//   - Botão "Publicar" em unidades AVAILABLE sem listing
//   - Botão "Despublicar" em listings ACTIVE

// Tab Configuração:
//   - Toggle: Activar integração imo.cv
//   - Toggle: Auto-publicar unidades disponíveis
//   - Campo: API Key imo.cv
//   - Botão "Testar ligação" → GET /api/v1/marketplace/ping/
```

---

## Verificação final

- [ ] `TenantSettings.imocv_enabled=True` para `demo_promotora`
- [ ] `sync_unit_listing.delay()` publica unidade no imo.cv local (porta 8000)
- [ ] Lead criado no imo.cv → webhook → Lead aparece no CRM ImoOS
- [ ] `ImoCvWebhookLog` criado para cada evento
- [ ] Webhook com assinatura inválida → 401 (não processa)
- [ ] `/marketplace` no frontend mostra listings sincronizados
- [ ] Tenant B não vê listings de Tenant A
- [ ] `sync_all_listings` Celery Beat: corre às 2h UTC-1 (3h UTC)
