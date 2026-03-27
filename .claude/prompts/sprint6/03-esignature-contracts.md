# Sprint 6 — E-Signature nos Contratos

## Contexto

Actualmente o fluxo de contratos é:
`DRAFT → ACTIVE` (manual, admin faz `activate`) → PDF gerado com WeasyPrint → S3

Este sprint adiciona **assinatura electrónica** nativa:
1. Comprador recebe link de assinatura por WhatsApp/email
2. Assina via browser (canvas ou serviço externo)
3. PDF assinado substitui o original no S3
4. Contrato transita automaticamente para ACTIVE

**Opção A (recomendada para MVP)**: assinatura simples interna — canvas HTML5,
PNG da assinatura incorporado no PDF WeasyPrint. Sem serviço externo.

**Opção B (produção)**: integrar DocuSign ou YouSign (configurável via env var).

Implementar Opção A neste sprint. Arquitectura preparada para Opção B.

## Pré-requisitos — Ler antes de começar

```
apps/contracts/models.py        → Contract (STATUS_DRAFT, STATUS_ACTIVE, pdf_s3_key)
apps/contracts/tasks.py         → generate_contract_pdf (WeasyPrint + S3)
apps/contracts/views.py         → ContractViewSet.activate
apps/crm/models.py              → Lead (email, phone para notificação)
apps/crm/views_public.py        → LeadCaptureView (padrão para endpoint público)
config/urls_public.py           → endpoints sem autenticação de tenant
```

```bash
grep "pdf_s3_key\|activate\|generate_contract_pdf" apps/contracts/models.py apps/contracts/views.py apps/contracts/tasks.py
cat config/urls_public.py
```

## Skills a carregar

```
@.claude/skills/16-security-compliance/webhook-verification/SKILL.md
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/02-backend-django/model-audit-history/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `model-architect` | SignatureRequest model + campos em Contract |
| `drf-viewset-builder` | Endpoint público de assinatura (sem auth JWT) |
| `celery-task-specialist` | Task: gerar PDF assinado + notificar |
| `react-component-builder` | Página pública de assinatura + canvas |

---

## Tarefa 1 — Modelo `SignatureRequest`

Prompt para `model-architect`:
> "Cria `SignatureRequest` em `apps/contracts/models.py`. Campos: `contract` (FK), `token` (UUIDField, único, gerado automaticamente), `expires_at` (DateTimeField, default=now+72h), `signed_at` (nullable), `signature_png_s3_key` (CharField, blank), `ip_address` (GenericIPAddressField, nullable), `signed_by_name` (CharField — comprador escreve o nome ao assinar), `status` (PENDING/SIGNED/EXPIRED/CANCELLED). TenantAwareModel + HistoricalRecords."

```python
class SignatureRequest(TenantAwareModel):
    STATUS_PENDING   = 'PENDING'
    STATUS_SIGNED    = 'SIGNED'
    STATUS_EXPIRED   = 'EXPIRED'
    STATUS_CANCELLED = 'CANCELLED'

    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name='signature_requests',
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    signed_at = models.DateTimeField(null=True, blank=True)
    signature_png_s3_key = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    signed_by_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            from django.utils import timezone
            self.expires_at = timezone.now() + timezone.timedelta(hours=72)
        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        from django.utils import timezone
        return timezone.now() > self.expires_at
```

**Campos adicionais em `Contract`:**
```python
# Adicionar a Contract:
signed_at = models.DateTimeField(null=True, blank=True)  # data efectiva de assinatura
signature_request = models.OneToOneField(
    'SignatureRequest', on_delete=models.SET_NULL, null=True, blank=True,
    related_name='signed_contract',
)
```

---

## Tarefa 2 — Endpoint público de assinatura

Prompt para `drf-viewset-builder`:
> "Cria views em `apps/contracts/views_public.py`:
> - `GET /sign/{token}/` → verifica token, retorna contrato (nome lead, unidade, valor) para renderizar na página de assinatura. 401 se expirado.
> - `POST /sign/{token}/` → recebe `{signature_png_base64: '...', signed_by_name: '...'}`. Valida token, guarda PNG no S3 (`tenants/{slug}/signatures/{token}.png`), marca `SignatureRequest.status=SIGNED`, enfileira `finalize_signed_contract.delay()`. Responde 200. Rate limit: 10 req/hora por IP (throttle)."

**Segurança crítica:**
```python
# NUNCA expor dados de outros contratos via token
# Token é UUIDv4 — 122 bits de entropia, não adivinható
# Verificar sempre: token existe + status=PENDING + não expirado
# Guardar IP para auditoria

def get_signature_request_or_404(token: str) -> SignatureRequest:
    try:
        sr = SignatureRequest.objects.select_related('contract__lead', 'contract__unit').get(
            token=token, status=SignatureRequest.STATUS_PENDING,
        )
    except SignatureRequest.DoesNotExist:
        raise Http404
    if sr.is_expired:
        sr.status = SignatureRequest.STATUS_EXPIRED
        sr.save(update_fields=['status'])
        raise ValidationError({'detail': 'Link de assinatura expirado.'})
    return sr
```

Registar em `config/urls_public.py`:
```python
path('sign/<uuid:token>/', SignatureView.as_view(), name='contract-sign'),
```

---

## Tarefa 3 — Celery task: finalizar contrato assinado

Prompt para `celery-task-specialist`:
> "Cria `finalize_signed_contract(tenant_schema, signature_request_id)` em `apps/contracts/tasks.py`. Dentro de `tenant_context`: (1) carrega SignatureRequest, (2) regenera PDF WeasyPrint incorporando PNG da assinatura e timestamp, (3) faz upload do PDF assinado para S3 (sobrepõe o original), (4) actualiza `contract.pdf_s3_key`, `contract.signed_at`, (5) chama `contract.activate()` se estava DRAFT, (6) notifica lead por WhatsApp com link S3 presignado. Retry ×3 backoff exponencial."

---

## Tarefa 4 — Action `request_signature` no ContractViewSet

**Ler `apps/contracts/views.py` antes de editar.**

```python
@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTenantAdmin])
def request_signature(self, request, pk=None):
    """
    Cria SignatureRequest e envia link ao comprador via WhatsApp.
    Idempotente: cancela request anterior se existir.
    """
    contract = self.get_object()
    if contract.status != Contract.STATUS_DRAFT:
        return Response({'detail': 'Apenas contratos DRAFT podem ser enviados para assinatura.'},
                        status=400)
    # Cancelar requests anteriores pendentes
    contract.signature_requests.filter(
        status=SignatureRequest.STATUS_PENDING,
    ).update(status=SignatureRequest.STATUS_CANCELLED)

    sr = SignatureRequest.objects.create(contract=contract)
    sign_url = f"{settings.PUBLIC_BASE_URL}/sign/{sr.token}/"

    # Enviar WhatsApp ao lead
    send_signature_request_whatsapp.delay(
        tenant_schema=connection.schema_name,
        signature_request_id=str(sr.id),
        sign_url=sign_url,
    )
    return Response({'signature_url': sign_url, 'expires_at': sr.expires_at})
```

---

## Tarefa 5 — Frontend: página pública de assinatura

Criar `frontend/src/app/sign/[token]/page.tsx` (rota pública — sem layout de autenticação):

```typescript
// Passo 1: GET /sign/{token}/ → mostrar resumo do contrato
//   - Nome do comprador, unidade, valor CVE, data de expiração
//
// Passo 2: Canvas HTML5 para assinatura manuscrita
//   - Botão "Limpar" + "Confirmar Assinatura"
//   - Campo: "Nome completo" (validação obrigatória)
//
// Passo 3: POST /sign/{token}/ com PNG base64
//   - Loading state enquanto processa
//   - Sucesso: "Contrato assinado com sucesso! Receberá o PDF no WhatsApp."
//   - Erro expirado: "Este link expirou. Contacte a promotora para novo link."

// Canvas helper:
const getSignaturePng = (canvas: HTMLCanvasElement): string => {
  return canvas.toDataURL('image/png').split(',')[1]; // base64 sem prefixo
};
```

---

## Verificação final

- [ ] `POST /api/v1/contracts/{id}/request_signature/` → cria SignatureRequest + WhatsApp
- [ ] `GET /sign/{token}/` → dados do contrato (sem auth JWT)
- [ ] `GET /sign/{token}/` com token expirado → 400
- [ ] `POST /sign/{token}/` → contrato passa a ACTIVE + PDF regenerado
- [ ] `POST /sign/{token}/` duas vezes → 404 (token já SIGNED)
- [ ] `/sign/{token}` no browser → canvas funcional em mobile
- [ ] IP guardado no SignatureRequest para auditoria
