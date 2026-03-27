# Sprint 7 - Prompt 03: Tenant Onboarding Flow - Implementação Concluída

## Resumo da Implementação

### ✅ Tarefas Completadas

#### 1. Modelo TenantRegistration
**Ficheiro:** `apps/tenants/models.py`

**Campos:**
- `company_name` - Nome da empresa
- `subdomain` - Subdomínio único (será schema_name)
- `plan` - starter/pro/enterprise
- `contact_email` - Email único para verificação
- `contact_name`, `contact_phone` - Dados de contacto
- `country` - País (CV, AO, SN)
- `verification_token` - UUID único
- `token_expires_at` - Expira em 48 horas
- `status` - PENDING/VERIFIED/PROVISIONING/ACTIVE/REJECTED
- `error_message` - Mensagem de erro se provisioning falhar

**Propriedades:**
- `is_token_expired` - Verifica expiração
- `schema_name` - Gera schema_name a partir do subdomain

---

#### 2. Endpoints Públicos de Registo
**Ficheiro:** `apps/tenants/views_public.py`

**Endpoints:**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/register/` | POST | Criar registo + enviar email verificação |
| `/api/v1/register/verify/` | GET | Verificar token + iniciar provisioning |
| `/api/v1/register/status/` | GET | Poll status do provisioning |

**Validações:**
- Subdomain: regex `^[a-z0-9][a-z0-9-]{1,28}[a-z0-9]$`
- Reservados: www, api, admin, mail, smtp, ftp, imos, app, localhost, static, media, cdn, dev, staging, prod
- Email único
- País: CV, AO, SN

---

#### 3. Celery Tasks de Provisioning
**Ficheiro:** `apps/tenants/tasks.py`

**Tasks:**

1. **`send_verification_email(registration_id)`**
   - Envia email com link de verificação
   - Template HTML profissional
   - Retry: 3x com 5 min delay

2. **`provision_tenant(registration_id)`**
   - Valida status VERIFIED
   - Cria Client (django-tenants cria schema)
   - Cria Domain primário
   - Cria TenantSettings com limites do plano
   - Cria admin user no schema do tenant
   - Cria TenantMembership
   - Envia email de credenciais
   - Actualiza status para ACTIVE
   - Cria PlanEvent
   - Timeout: 120s
   - Retry: 1x (idempotente)

3. **`send_credentials_email(registration_id, password, domain)`**
   - Envia email com credenciais
   - Password temporária
   - URL de login
   - Retry: 2x

4. **`cleanup_expired_registrations()`**
   - Delete PENDING registos > 7 dias
   - Corre diariamente (Celery Beat)

**Helpers:**
- `get_max_projects_for_plan()`
- `get_max_units_for_plan()`
- `get_max_users_for_plan()`

---

#### 4. Frontend /register
**Ficheiro:** `frontend/src/app/register/page.tsx`

**Multi-step form:**

**Step 1 - Empresa:**
- Nome da empresa
- Subdomínio + validação em tempo real
- País (select)

**Step 2 - Contacto:**
- Nome completo
- Email profissional
- WhatsApp/Telefone

**Step 3 - Plano:**
- 3 cards: Starter (verde), Pro (azul), Enterprise (roxo)
- Features por plano
- Preço

**Step 4 - Confirmação:**
- "Verifique o seu email"
- Instruções
- Link para login

---

#### 5. Frontend /verify-email
**Ficheiro:** `frontend/src/app/verify-email/page.tsx`

**Estados:**
- `loading` - A carregar
- `verifying` - A verificar token
- `success` - Email verificado, provisioning iniciado
- `already_verified` - Email já verificado anteriormente
- `already_active` - Conta já está activa
- `expired` - Token expirado (>48h)
- `error` - Erro genérico

**UI:**
- Ícones emoji por estado
- Mensagens claras em pt-PT
- Redirect para login após sucesso

---

#### 6. Email Templates
**Directório:** `apps/tenants/templates/tenants/emails/`

**Templates:**

1. **`verification_email.html`**
   - Header com gradiente azul
   - Detalhes do registo (empresa, subdomain, plano)
   - Botão CTA "Verificar Email"
   - Link completo em código
   - Aviso de expiração (48h)
   - Footer com suporte

2. **`credentials_email.html`**
   - Header verde (sucesso)
   - Caixa amarela com credenciais
   - Email e password temporária
   - Botão "Fazer Login"
   - Próximos passos
   - Aviso de segurança (alterar password)

---

### 🔧 Alterações Técnicas

#### URLs Públicas
**Ficheiro:** `config/urls_public.py`

Adicionado:
```python
path('api/v1/register/', TenantRegistrationCreateView.as_view()),
path('api/v1/register/verify/', TenantRegistrationVerifyView.as_view()),
path('api/v1/register/status/', TenantRegistrationStatusView.as_view()),
```

#### Middleware Frontend
**Ficheiro:** `frontend/src/middleware.ts`

Adicionado às rotas públicas:
```typescript
"/register",      // Self-service registration
"/verify-email",  // Email verification
```

---

## Fluxo Completo

```
1. Utilizador preenche formulário /register
   ↓
2. POST /api/v1/register/
   → Cria TenantRegistration (status=PENDING)
   → Queue: send_verification_email
   ↓
3. Utilizador recebe email
   ↓
4. Clica em link → /verify-email?token={uuid}
   ↓
5. GET /api/v1/register/verify/
   → Valida token
   → Status = VERIFIED
   → Queue: provision_tenant
   ↓
6. Task provision_tenant:
   → Cria Client + schema
   → Cria Domain
   → Cria TenantSettings
   → Cria User + Membership
   → Queue: send_credentials_email
   → Status = ACTIVE
   ↓
7. Utilizador recebe email com credenciais
   ↓
8. Login com email/password
   ↓
9. Dashboard do tenant
```

---

## Comandos de Verificação

### 1. Testar registo via API
```bash
curl -X POST http://localhost:8000/api/v1/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Teste Lda",
    "subdomain": "teste-empresa",
    "plan": "starter",
    "contact_email": "teste@empresa.cv",
    "contact_name": "João Teste",
    "contact_phone": "+238991234567",
    "country": "CV"
  }'
```

### 2. Testar verificação
```bash
curl "http://localhost:8000/api/v1/register/verify/?token={token-do-email}"
```

### 3. Verificar status
```bash
curl "http://localhost:8000/api/v1/register/status/?token={token}"
```

### 4. Verificar tasks Celery
```bash
docker logs imos-celery-1 | grep "provision_tenant"
```

### 5. Verificar tenant criado
```bash
docker exec -it imos-web-1 python manage.py shell
>>> from apps.tenants.models import Client
>>> Client.objects.all()
```

---

## Próximos Passos (Sprint 7)

Restam 2 prompts:

| # | Prompt | Prioridade | Descrição |
|---|--------|------------|-----------|
| 01 | Frontend Tests | 🟠 Alta | Vitest + Testing Library |
| 04 | Reports & Exports | 🟡 Média | PDF/Excel exports |
| 05 | Security Hardening | 🟡 Média | Pentest + rate limiting |

---

**Implementado por:** Tech Lead Agent  
**Data:** 15 Mar 2026  
**Status:** ✅ Completo
