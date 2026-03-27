# Sprint 7 — Tenant Onboarding Flow (Self-Service)

## Contexto

Actualmente criar um tenant requer o comando `manage.py create_tenant` (manual).
Este sprint implementa **onboarding self-service**:
1. Promotora preenche formulário público (nome, email, subdomínio)
2. Recebe email de verificação
3. Escolhe plano (Starter gratuito, Pro pago)
4. Tenant criado automaticamente via Celery task
5. Admin da promotora recebe credenciais por email + WhatsApp

É o fluxo de entrada principal para novos clientes ImoOS.

## Pré-requisitos — Ler antes de começar

```
apps/tenants/models.py          → Client, TenantSettings, PlanEvent
apps/tenants/management/commands/create_tenant.py → lógica actual
config/urls_public.py           → endpoints sem tenant
config/settings/base.py         → EMAIL_HOST, DEFAULT_FROM_EMAIL
apps/users/models.py            → User model
```

```bash
cat apps/tenants/management/commands/create_tenant.py
grep "email\|EMAIL" config/settings/base.py
cat config/urls_public.py
```

## Skills a carregar

```
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
@.claude/skills/16-security-compliance/webhook-verification/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `model-architect` | TenantRegistration (registo pendente) |
| `drf-viewset-builder` | Endpoint público de registo |
| `celery-task-specialist` | Task: provision_tenant (criar tenant + notificar) |
| `nextjs-tenant-routing` | Página pública /register + /verify-email |
| `react-component-builder` | Formulário de registo multi-step |

---

## Tarefa 1 — Modelo TenantRegistration

Prompt para `model-architect`:
> "Cria `TenantRegistration` em `apps/tenants/models.py`. SHARED_APP (não TENANT_APP). Campos: `company_name` (CharField), `subdomain` (CharField único — será o schema_name), `plan` (starter/pro/enterprise), `contact_email` (EmailField), `contact_name` (CharField), `contact_phone` (CharField), `country` (CharField, default=CV), `verification_token` (UUIDField, default=uuid4), `token_expires_at` (DateTimeField), `status` (PENDING_VERIFICATION/VERIFIED/PROVISIONING/ACTIVE/REJECTED), `error_message` (TextField), `created_at`, `provisioned_at`. SEM HistoricalRecords (log de estado é suficiente)."

```python
class TenantRegistration(models.Model):
    STATUS_PENDING  = 'PENDING_VERIFICATION'
    STATUS_VERIFIED = 'VERIFIED'
    STATUS_PROV     = 'PROVISIONING'
    STATUS_ACTIVE   = 'ACTIVE'
    STATUS_REJECTED = 'REJECTED'

    company_name       = models.CharField(max_length=200)
    subdomain          = models.CharField(max_length=63, unique=True)  # RFC 1123
    plan               = models.CharField(max_length=20, choices=PLAN_CHOICES, default='starter')
    contact_email      = models.EmailField(unique=True)
    contact_name       = models.CharField(max_length=200)
    contact_phone      = models.CharField(max_length=20)
    country            = models.CharField(max_length=2, default='CV')
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    token_expires_at   = models.DateTimeField()
    status             = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message      = models.TextField(blank=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    provisioned_at     = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token_expires_at:
            from django.utils import timezone
            self.token_expires_at = timezone.now() + timezone.timedelta(hours=48)
        super().save(*args, **kwargs)

    @property
    def is_token_expired(self):
        from django.utils import timezone
        return timezone.now() > self.token_expires_at
```

---

## Tarefa 2 — Endpoint público de registo

Prompt para `drf-viewset-builder`:
> "Cria views em `apps/tenants/views_public.py`:
> - `POST /api/v1/register/` — recebe `{company_name, subdomain, plan, contact_email, contact_name, contact_phone}`. Valida subdomain (regex `^[a-z0-9-]{3,30}$`, sem conflito). Cria `TenantRegistration`. Enfileira `send_verification_email.delay(registration_id)`. Responde 201.
> - `GET /api/v1/register/verify/?token={uuid}` — valida token, marca `status=VERIFIED`, enfileira `provision_tenant.delay(registration_id)`. Responde 200 ou 400 (token expirado)."

```python
# Validação de subdomain:
SUBDOMAIN_RE = re.compile(r'^[a-z0-9][a-z0-9-]{1,28}[a-z0-9]$')

def validate_subdomain(value):
    if not SUBDOMAIN_RE.match(value):
        raise ValidationError('Subdomínio inválido. Use apenas letras minúsculas, números e hífens (3-30 caracteres).')
    if Client.objects.filter(schema_name=value.replace('-', '_')).exists():
        raise ValidationError('Este subdomínio já está em uso.')
    if value in ('www', 'api', 'admin', 'mail', 'smtp', 'ftp', 'imos', 'app'):
        raise ValidationError('Este subdomínio está reservado.')
```

---

## Tarefa 3 — Celery tasks de provisioning

Prompt para `celery-task-specialist`:
> "Cria 3 tasks em `apps/tenants/tasks.py`:

> `send_verification_email(registration_id)`: envia email com link `{FRONTEND_URL}/verify-email?token={token}` a `contact_email`. Template HTML simples. Retry ×3.

> `provision_tenant(registration_id)`: (1) valida que registration.status=VERIFIED, (2) constrói `schema_name=subdomain.replace('-','_')`, (3) chama `Client.objects.create(...)` — django-tenants cria schema automaticamente, (4) cria Domain, TenantSettings, admin User, TenantMembership, (5) envia credenciais por email E WhatsApp, (6) actualiza `registration.status=ACTIVE`, `provisioned_at=now()`. Em caso de erro: `registration.status=REJECTED`, `error_message=str(e)`. Timeout: 120s. Retry ×1 (provisionamento é idempotente com verificação prévia).

> `cleanup_expired_registrations()`: corre diariamente. Remove registros PENDING_VERIFICATION com token expirado há mais de 7 dias."

---

## Tarefa 4 — Frontend: /register (público)

Criar `frontend/src/app/register/page.tsx` (sem autenticação, sem middleware block):

```typescript
// Step 1: Dados da empresa
//   - Nome da empresa (required)
//   - Subdomínio (required) + validação em tempo real: "empresa.imos.cv"
//   - País (Select: Cabo Verde/Angola/Senegal)
//
// Step 2: Contacto
//   - Nome completo (required)
//   - Email profissional (required)
//   - WhatsApp / Telefone (required)
//
// Step 3: Plano
//   - Cards de plano: Starter (gratuito, 3 proj, 150 unidades)
//                     Pro (€49/mês, 20 proj, 1000 unidades)
//                     Enterprise (contactar comercial)
//   - Botão "Criar Conta Gratuita" (Starter) ou "Iniciar Trial Pro" (Pro)
//
// Step 4: Confirmação
//   - "Enviámos um email de verificação para {email}"
//   - "Verifique também o WhatsApp"

// Adicionar ao middleware.ts como rota pública:
// '/register', '/verify-email'
```

Criar `frontend/src/app/verify-email/page.tsx`:
```typescript
// Lê ?token= da URL
// GET /api/v1/register/verify/?token={token}
// Sucesso: "A sua conta está a ser configurada! Receberá as credenciais em breve."
// Erro: "Link inválido ou expirado. Solicite novo link."
```

---

## Tarefa 5 — Email template

Criar `apps/tenants/email_templates/verification_email.html`:
```html
<!DOCTYPE html>
<html>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
  <img src="{{ LOGO_URL }}" alt="ImoOS" height="40">
  <h2>Bem-vindo ao ImoOS, {{ company_name }}!</h2>
  <p>Clique no botão abaixo para verificar o seu email e activar a conta.</p>
  <a href="{{ verification_url }}"
     style="background:#2563eb;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block;">
    Verificar Email
  </a>
  <p style="color:#666;font-size:12px;margin-top:20px;">
    Este link expira em 48 horas. Se não criou esta conta, ignore este email.
  </p>
</body>
</html>
```

---

## Verificação final

- [ ] `POST /api/v1/register/` com dados válidos → 201, email enviado
- [ ] `POST /api/v1/register/` com subdomínio duplicado → 400 com mensagem clara
- [ ] `GET /api/v1/register/verify/?token={valid}` → 200, task provision_tenant enfileirada
- [ ] `GET /api/v1/register/verify/?token={expired}` → 400
- [ ] `provision_tenant` cria schema PostgreSQL, User, TenantMembership
- [ ] Admin recebe credenciais por email
- [ ] `/register` acessível sem autenticação
- [ ] `/verify-email?token=...` funcional no browser
- [ ] Subdomínio reservados (www, api, admin) → rejeitado
