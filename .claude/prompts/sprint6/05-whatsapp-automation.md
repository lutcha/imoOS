# Sprint 6 — WhatsApp Automation (Templates por Tenant)

## Contexto

O ImoOS já envia WhatsApp ad-hoc (notificação de lead, lembrete de pagamento).
Este sprint estrutura os templates oficiais da Meta Cloud API por tenant:
- Templates aprovados pela Meta (HSM — Highly Structured Messages)
- Variáveis dinâmicas por tenant (nome da empresa, assinatura, logo)
- Log de todas as mensagens enviadas (auditoria LGPD)
- Opt-out de leads (Lei n.º 133/V/2019 Cabo Verde — equivalente RGPD)

`TenantSettings.whatsapp_phone_id` já existe.

## Pré-requisitos — Ler antes de começar

```
apps/tenants/models.py          → TenantSettings.whatsapp_phone_id
apps/crm/models.py              → Lead (phone, opt_out_whatsapp se existir)
apps/crm/tasks.py               → notify_whatsapp_new_lead (padrão actual)
config/settings/base.py         → WHATSAPP_* env vars
```

```bash
grep "whatsapp\|WHATSAPP" apps/crm/tasks.py apps/tenants/models.py config/settings/base.py
grep "opt_out\|phone" apps/crm/models.py
```

## Skills a carregar

```
@.claude/skills/09-integrations/whatsapp-cloud-api/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
@.claude/skills/16-security-compliance/webhook-verification/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `model-architect` | WhatsAppMessage (log) + WhatsAppTemplate models |
| `celery-task-specialist` | send_whatsapp_template task (substituir ad-hoc) |
| `drf-viewset-builder` | Webhook de opt-out + status delivery |
| `react-component-builder` | Página /settings/whatsapp — gerir templates |

---

## Tarefa 1 — Modelos de log e templates

Prompt para `model-architect`:
> "Cria `WhatsAppMessage` e `WhatsAppTemplate` em `apps/crm/models.py` (ou `apps/notifications/models.py` se preferires app dedicada). `WhatsAppTemplate`: nome (CharField único por tenant), template_id_meta (CharField — ID na Meta), variáveis (JSONField com {key: description}), idioma (pt_PT/pt_BR/en_US), activo (Boolean). `WhatsAppMessage`: FK Lead (nullable — pode ser a admins), template FK nullable, telefone_destino, payload_enviado (JSONField), status (SENT/DELIVERED/READ/FAILED), message_id_meta (CharField), sent_at, delivered_at, read_at, error (TextField). TenantAwareModel em ambos."

```python
class WhatsAppTemplate(TenantAwareModel):
    name = models.CharField(max_length=100)          # ex: 'novo_lead', 'lembrete_pagamento'
    template_id_meta = models.CharField(max_length=100)  # ID registado na Meta
    language = models.CharField(max_length=10, default='pt_PT')
    variables = models.JSONField(default=dict)        # {1: "nome_lead", 2: "nome_unidade"}
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [('name',)]  # único por schema (tenant)


class WhatsAppMessage(TenantAwareModel):
    STATUS_SENT      = 'SENT'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_READ      = 'READ'
    STATUS_FAILED    = 'FAILED'

    lead = models.ForeignKey('Lead', on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey(WhatsAppTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_SENT)
    message_id_meta = models.CharField(max_length=100, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True)
```

---

## Tarefa 2 — Opt-out de WhatsApp nos Leads

**Ler `apps/crm/models.py` antes de editar.**

Adicionar ao modelo `Lead`:
```python
whatsapp_opt_out = models.BooleanField(
    default=False,
    help_text='Lead pediu para não receber mensagens WhatsApp (LGPD/Lei 133/V/2019)',
)
whatsapp_opt_out_at = models.DateTimeField(null=True, blank=True)
```

**Regra**: qualquer função de envio de WhatsApp DEVE verificar `lead.whatsapp_opt_out`
antes de enviar. Se `True`, registar `WhatsAppMessage(status=FAILED, error='opt_out')` e
não chamar a API da Meta.

---

## Tarefa 3 — Cliente WhatsApp Cloud API

Criar `apps/crm/whatsapp_client.py` (ou `apps/notifications/whatsapp_client.py`):

```python
"""
WhatsApp Cloud API client.
Docs: https://developers.facebook.com/docs/whatsapp/cloud-api/

NUNCA hardcodar o token — vem de settings.WHATSAPP_ACCESS_TOKEN (env var).
NUNCA enviar para leads com opt_out=True.
"""
import requests
from django.conf import settings


class WhatsAppCloudClient:
    BASE_URL = 'https://graph.facebook.com/v18.0'

    def __init__(self, phone_number_id: str):
        self.phone_number_id = phone_number_id
        self.session = requests.Session()
        self.session.headers['Authorization'] = f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}'
        self.session.headers['Content-Type'] = 'application/json'

    def send_template(
        self,
        to: str,
        template_name: str,
        language: str,
        components: list[dict],
    ) -> dict:
        """
        Envia template HSM aprovado pela Meta.
        `components`: lista de {type: 'body', parameters: [{type: 'text', text: '...'}]}
        Retorna {messages: [{id: 'wamid...'}]} ou lança requests.HTTPError.
        """
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': language},
                'components': components,
            },
        }
        resp = self.session.post(
            f'{self.BASE_URL}/{self.phone_number_id}/messages',
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def send_text(self, to: str, body: str) -> dict:
        """Para mensagens não-template (sessão activa de 24h). Usar com moderação."""
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'text',
            'text': {'body': body},
        }
        resp = self.session.post(
            f'{self.BASE_URL}/{self.phone_number_id}/messages',
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
```

---

## Tarefa 4 — Celery task unificada para WhatsApp

Prompt para `celery-task-specialist`:
> "Cria `send_whatsapp_template(tenant_schema, lead_id, template_name, variables)` em `apps/crm/tasks.py`. Dentro de `tenant_context`: (1) carrega Lead, verifica `whatsapp_opt_out` — se True, loga e retorna; (2) carrega `TenantSettings.whatsapp_phone_id`; (3) carrega `WhatsAppTemplate` pelo nome; (4) constrói components com variáveis; (5) chama `WhatsAppCloudClient.send_template()`; (6) cria `WhatsAppMessage(status=SENT, message_id_meta=...)`; (7) em caso de erro: cria `WhatsAppMessage(status=FAILED, error=str(e))`. Retry ×3 backoff exponencial. Idempotente: não reenviar se já existe WhatsAppMessage SENT/DELIVERED para este lead+template nas últimas 24h."

**Substituir `notify_whatsapp_new_lead` pelo novo padrão:**
```python
# Antes (ad-hoc, sem log):
# send_whatsapp(phone, f"Novo lead: {lead.name}")

# Depois (template + log):
send_whatsapp_template.delay(
    tenant_schema=schema,
    lead_id=str(lead.id),
    template_name='novo_lead',
    variables={'1': lead.full_name, '2': lead.source},
)
```

---

## Tarefa 5 — Webhook de entrega e opt-out

Prompt para `drf-viewset-builder`:
> "Cria `WhatsAppWebhookView` em `apps/crm/views_public.py`. `GET /api/v1/webhooks/whatsapp/` → verificação do hub Meta (query params `hub.mode`, `hub.challenge`, `hub.verify_token`). `POST /api/v1/webhooks/whatsapp/` → recebe eventos de entrega (statuses: delivered, read) e opt-out (mensagem 'STOP'). Verificar assinatura `X-Hub-Signature-256` com HMAC-SHA256. Processar assincronamente com `process_whatsapp_webhook.delay()`."

**Verificação de assinatura Meta (obrigatória):**
```python
def verify_meta_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f'sha256={expected}', signature)
```

**Processar opt-out:**
```python
# Se mensagem recebida contém 'STOP' ou 'PARAR':
Lead.objects.filter(phone=from_phone).update(
    whatsapp_opt_out=True,
    whatsapp_opt_out_at=timezone.now(),
)
```

---

## Tarefa 6 — Frontend: /settings/whatsapp

Criar `frontend/src/app/settings/whatsapp/page.tsx`:

```typescript
// Secção: Configuração
//   - Phone Number ID (read de TenantSettings)
//   - Status da integração: ✅ Activo / ❌ Não configurado

// Secção: Templates registados
//   - Tabela: Nome | Template Meta ID | Idioma | Activo
//   - Toggle activo/inactivo
//   - Botão "Sincronizar com Meta" (futuro)

// Secção: Log de mensagens (últimas 50)
//   - Tabela: Lead | Telefone | Template | Estado | Data
//   - Filtro por estado (SENT/DELIVERED/READ/FAILED)
//   - Badge de estado com cor (DELIVERED=verde, FAILED=vermelho)
```

---

## Verificação final

- [ ] `send_whatsapp_template.delay()` com lead `opt_out=True` → não envia, log FAILED(opt_out)
- [ ] Template enviado → `WhatsAppMessage` criado com `message_id_meta`
- [ ] `POST /api/v1/webhooks/whatsapp/` com status=delivered → `WhatsAppMessage.delivered_at` actualizado
- [ ] `POST /api/v1/webhooks/whatsapp/` com assinatura inválida → 401
- [ ] Mensagem "STOP" → `lead.whatsapp_opt_out=True`
- [ ] `GET /api/v1/webhooks/whatsapp/?hub.mode=subscribe&hub.challenge=12345` → 200 com `12345`
- [ ] Log de mensagens visível em `/settings/whatsapp`
- [ ] Tenant A não vê logs de Tenant B
