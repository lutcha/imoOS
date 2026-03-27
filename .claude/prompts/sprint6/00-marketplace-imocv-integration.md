# Sprint 6 — Integração imo.cv Marketplace

## Contexto

imo.cv é o principal marketplace imobiliário de Cabo Verde. A integração permite:
1. **Publicar unidades** do ImoOS directamente no imo.cv
2. **Receber leads** capturados no imo.cv no CRM do ImoOS
3. **Sincronizar status** de disponibilidade (AVAILABLE/RESERVED/SOLD) em tempo real

`apps/marketplace/` existe mas está vazio.

**IMPORTANTE:** A documentação da API imo.cv é necessária antes deste prompt.
Verificar com o PO se existe acesso ao sandbox/staging da API.

## Pré-requisitos — Ler antes de começar

```
apps/inventory/models.py     → Unit, status choices
apps/crm/models.py           → Lead, SOURCE_CHOICES (adicionar 'IMOCV')
apps/crm/views_public.py     → LeadCaptureView (padrão para webhook)
apps/crm/tasks.py            → notify_whatsapp_new_lead (padrão de task)
apps/tenants/models.py       → TenantSettings (adicionar imocv_api_key)
config/settings/base.py      → TENANT_APPS
```

```bash
ls apps/marketplace/
grep "SOURCE_CHOICES\|IMOCV" apps/crm/models.py
grep "marketplace" config/settings/base.py
```

## Skills a carregar

```
@.claude/skills/13-module-marketplace/imocv-sync/SKILL.md
@.claude/skills/13-module-marketplace/lead-source-tracking/SKILL.md
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/16-security-compliance/webhook-verification/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `model-architect` | MarketplaceListing + ImoCvWebhookLog models |
| `drf-viewset-builder` | ListingViewSet + webhook endpoint público |
| `celery-task-specialist` | sync_unit_to_imocv + sync_all_listings (periodic) |
| `isolation-test-writer` | Testes de isolamento do marketplace |

---

## Tarefa 1 — Modelos (`apps/marketplace/models.py`)

Prompt para `model-architect`:
> "Cria `MarketplaceListing` e `ImoCvWebhookLog` para ImoOS em `apps/marketplace/`. `MarketplaceListing`: OneToOne com `Unit`, imocv_listing_id (CharField, nullable), status (PENDING_SYNC/PUBLISHED/PAUSED/REMOVED), last_synced_at, sync_error, price_override_cve (nullable — se None usa Unit.pricing). `ImoCvWebhookLog`: tenant FK, event_type, payload (JSONField), processed_at, error. Ambos com TenantAwareModel."

```python
class MarketplaceListing(TenantAwareModel):
    STATUS_PENDING   = 'PENDING_SYNC'
    STATUS_PUBLISHED = 'PUBLISHED'
    STATUS_PAUSED    = 'PAUSED'
    STATUS_REMOVED   = 'REMOVED'

    unit = models.OneToOneField('inventory.Unit', on_delete=models.CASCADE, related_name='listing')
    imocv_listing_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    sync_error = models.TextField(blank=True)
    price_override_cve = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()
```

---

## Tarefa 2 — Serviço de integração (`apps/marketplace/imocv_client.py`)

```python
# Client HTTP para a API imo.cv
# Autenticação: Bearer token por tenant (TenantSettings.imocv_api_key)
# NUNCA hardcodar credenciais — vêm de TenantSettings ou env vars

class ImoCvClient:
    BASE_URL = settings.IMOCV_API_BASE_URL  # env var

    def __init__(self, api_key: str):
        self.session = requests.Session()
        self.session.headers['Authorization'] = f'Bearer {api_key}'
        self.session.headers['Content-Type'] = 'application/json'

    def publish_unit(self, unit: 'Unit', price_cve: Decimal) -> dict:
        """Publica ou actualiza unidade no imo.cv. Retorna imocv_listing_id."""

    def update_availability(self, imocv_listing_id: str, available: bool) -> None:
        """Actualiza disponibilidade sem alterar os dados do anúncio."""

    def remove_listing(self, imocv_listing_id: str) -> None:
        """Remove o anúncio (não apaga a Unit local)."""
```

---

## Tarefa 3 — Celery tasks (`apps/marketplace/tasks.py`)

Prompt para `celery-task-specialist`:
> "Cria 3 tasks em `apps/marketplace/tasks.py` para ImoOS:
> 1. `sync_unit_listing(tenant_schema, unit_id)` — idempotente: publica se PENDING, actualiza se PUBLISHED, remove se unit.status=SOLD. Retry ×3 com backoff.
> 2. `sync_all_listings(tenant_schema)` — varre todas as MarketplaceListing PUBLISHED e actualiza disponibilidade. Corre de hora em hora por tenant.
> 3. `process_imocv_webhook(tenant_schema, webhook_log_id)` — processa ImoCvWebhookLog: evento 'lead_captured' cria Lead com source='IMOCV', evento 'unit_viewed' incrementa counter."

---

## Tarefa 4 — Webhook público (receber leads do imo.cv)

Prompt para `drf-viewset-builder`:
> "Cria `ImoCvWebhookView` em `apps/marketplace/views.py`. Endpoint: `POST /api/v1/marketplace/webhook/imocv/`. Autenticação: verificar header `X-ImoCv-Signature` com HMAC-SHA256 usando `settings.IMOCV_WEBHOOK_SECRET`. Se assinatura inválida → 401. Guardar payload em `ImoCvWebhookLog`, encolar `process_imocv_webhook.delay()`. Responder sempre 200 imediatamente (webhook idempotente)."

**Verificação HMAC (segurança crítica):**
```python
import hashlib, hmac

def verify_imocv_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f'sha256={expected}', signature)
```

---

## Tarefa 5 — TenantSettings: chave API imo.cv

**Ler `apps/tenants/models.py` antes de editar.**

Adicionar ao modelo `TenantSettings`:
```python
imocv_api_key = models.CharField(max_length=200, blank=True)
imocv_enabled = models.BooleanField(default=False)
imocv_auto_publish = models.BooleanField(
    default=False,
    help_text='Publicar automaticamente unidades AVAILABLE no imo.cv',
)
```

Actualizar a tab "Integrações" no `/settings` para incluir o campo da chave API.

---

## Tarefa 6 — Frontend: Gestão de listings

Criar `frontend/src/app/marketplace/page.tsx`:
- Tabela: Unidade | Projecto | Estado imo.cv | Último Sync | Preço Publicado
- Toggle: activar/pausar listing
- Botão "Sincronizar tudo"
- Badge de erro se `sync_error` não vazio

---

## Verificação final

- [ ] `POST /api/v1/marketplace/webhook/imocv/` com assinatura inválida → 401
- [ ] `POST /api/v1/marketplace/webhook/imocv/` com payload válido → 200 + Lead criado com source='IMOCV'
- [ ] `sync_unit_listing.delay(schema, unit_id)` publica no imo.cv (sandbox)
- [ ] Unit muda para RESERVED → imo.cv actualizado automaticamente
- [ ] `pytest tests/tenant_isolation/test_marketplace_isolation.py -v`
