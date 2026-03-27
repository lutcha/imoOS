# Sprint 7 - Prompt 02: Admin Backoffice - Implementação Concluída

## Resumo da Implementação

### ✅ Tarefas Completadas

#### 1. Django Admin Customizado
**Ficheiros criados/modificados:**
- `apps/tenants/admin.py` (novo) - Configuração completa do Django Admin
- `config/urls.py` - URL customizável via `DJANGO_SUPERADMIN_URL`
- `config/settings/base.py` - Variável `DJANGO_SUPERADMIN_URL`

**Funcionalidades:**
- Listagem de tenants com health check
- Filtros por plano, estado, país
- Busca por nome, schema, slug
- Acções em batch: suspender/activar tenants
- Exportação CSV de tenants
- Admin imutável para PlanEvents (audit log)

**Modelos registados:**
- `Client` (Tenant) - com health check e acções
- `Domain` - com prevenção de delete de primary domain
- `TenantSettings` - configuração por tenant
- `PlanEvent` - audit log imutável

---

#### 2. SuperAdmin API
**Ficheiros modificados:**
- `apps/tenants/views.py` - Adicionado `SuperAdminTenantViewSet` e `TenantAdminSerializer`
- `apps/tenants/urls.py` - Router para endpoints superadmin
- `apps/users/serializers.py` - Adicionado `is_staff` às claims JWT

**Endpoints criados:**

| Endpoint | Método | Auth | Descrição |
|----------|--------|------|-----------|
| `/api/v1/tenants/superadmin/tenants/` | GET | IsAdminUser | Listar todos os tenants com contagens de recursos |
| `/api/v1/tenants/superadmin/tenants/{id}/` | GET | IsAdminUser | Detalhes de um tenant |
| `/api/v1/tenants/superadmin/tenants/{id}/suspend/` | POST | IsAdminUser | Suspender tenant |
| `/api/v1/tenants/superadmin/tenants/{id}/activate/` | POST | IsAdminUser | Activar tenant |
| `/api/v1/tenants/superadmin/tenants/platform_summary/` | GET | IsAdminUser | Métricas agregadas da plataforma |

**TenantAdminSerializer inclui:**
- Dados básicos do tenant
- Domain primário
- Contagens de recursos (users, projects, units) por schema
- Plano, estado, país

---

#### 3. Frontend /superadmin/
**Ficheiros criados:**
- `frontend/src/app/superadmin/layout.tsx` - Layout com protecção is_staff
- `frontend/src/app/superadmin/page.tsx` - Dashboard completo

**Funcionalidades do Dashboard:**

**KPI Cards:**
- Total de tenants (activos/inactivos)
- Contagem por plano (Starter, Pro, Enterprise)

**Recursos da Plataforma:**
- Total de projectos
- Total de unidades
- Total de utilizadores

**Tabela de Tenants:**
- Nome da empresa + domain
- Schema name
- Plano (badge colorido)
- País
- Recursos (users, projects, units)
- Estado (activo/suspenso)
- Acções (suspender/activar, visitar)

**Navegação:**
- Link para Django Admin
- Link para Health Check
- Link para Prometheus Metrics
- Voltar ao Dashboard

---

#### 4. Superuser de Plataforma
**Ficheiros criados:**
- `apps/core/management/commands/create_platform_admin.py`

**Utilização:**
```bash
# Interactivo (pede password)
python manage.py create_platform_admin

# Com environment variables
PLATFORM_ADMIN_EMAIL=admin@imos.cv
PLATFORM_ADMIN_PASSWORD=SecurePass123
python manage.py create_platform_admin
```

**Funcionalidades:**
- Cria utilizador com `is_staff=True` e `is_superuser=True`
- Detecta se utilizador já existe e faz upgrade
- Validação de password (min 8 caracteres)
- Mensagens de sucesso com instruções

---

### 🔧 Alterações Técnicas

#### Backend

**JWT Claims (Sprint 7):**
```python
# apps/users/serializers.py
token['is_staff'] = user.is_staff  # Nova claim
```

**UserSerializer:**
```python
fields = [..., 'is_staff', ...]  # Adicionado
```

#### Frontend

**AuthContext actualizado:**
```typescript
interface JwtClaims {
  is_staff: boolean;  // Nova claim
}

interface User {
  isStaff: boolean;  // Novo campo
}
```

---

## Variáveis de Ambiente

Adicionar ao `.env`:
```bash
# Django Super Admin URL
DJANGO_SUPERADMIN_URL=django-admin/

# Opcional: criar super-admin automático
PLATFORM_ADMIN_EMAIL=superadmin@imos.cv
PLATFORM_ADMIN_PASSWORD=YourSecurePassword123
```

---

## Comandos de Verificação

### 1. Criar super-admin
```bash
docker exec -it imos-web-1 python manage.py create_platform_admin
```

### 2. Testar Django Admin
```
http://localhost:8000/django-admin/
Login com credenciais do super-admin
→ Deve mostrar "Clientes (Tenants)" no sidebar
```

### 3. Testar Super Admin Dashboard
```
http://localhost:3000/superadmin/
→ Deve mostrar dashboard com KPIs e tabela de tenants
→ Utilizador não-staff é redirect para /
```

### 4. Testar API SuperAdmin
```bash
# Obter token de super-admin
curl -X POST http://localhost:8000/api/v1/users/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@imos.cv","password":"SecurePass123"}'

# Usar token para listar tenants
curl http://localhost:8000/api/v1/tenants/superadmin/tenants/ \
  -H "Authorization: Bearer <token>"

# Obter platform summary
curl http://localhost:8000/api/v1/tenants/superadmin/tenants/platform_summary/ \
  -H "Authorization: Bearer <token>"
```

---

## Segurança

### Protecções Implementadas

1. **is_staff verification**
   - Backend: `IsAdminUser` permission em todos os endpoints
   - Frontend: Redirect automático se `!user.isStaff`

2. **Schema isolation**
   - SuperAdmin API opera sempre no schema público
   - Contagens de recursos usam `schema_context()` temporário

3. **Audit logging**
   - Suspensão/activação de tenants cria `PlanEvent`
   - Django Admin logs todas as acções

4. **Immutable audit log**
   - `PlanEventAdmin` não permite editar/apagar eventos

---

## Próximos Passos (Sprint 7)

### Prompt 03: Tenant Onboarding Flow
- Self-service registration público
- Email verification
- Automatic tenant provisioning
- Integração com pagamentos (Stripe/MBE)

### Prompt 01: Frontend Tests
- Vitest + Testing Library setup
- Testes de componentes React
- Coverage ≥80% em componentes core

### Prompt 04: Reports & Exports
- PDF exports (vendas, projectos)
- Excel exports (unidades, CRM)
- Celery tasks para exports grandes

### Prompt 05: Security Hardening
- Rate limiting audit
- OWASP security scan
- Pentest básico

---

**Implementado por:** Tech Lead Agent  
**Data:** 15 Mar 2026  
**Status:** ✅ Completo
