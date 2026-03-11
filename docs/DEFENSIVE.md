# ImoOS — Instruções Defensivas

> Regras não-negociáveis para toda a equipa. Violações bloqueiam merge.

---

## 1. LEITURA ANTES DE ESCREVER

**Regra:** Nunca modificar um ficheiro sem o ler primeiro na íntegra.

```
❌ Escrever models.py sem ler o existente
✅ Ler → entender → editar apenas o necessário
```

- Se o ficheiro está vazio, verificar se há uma skill relevante em `.claude/skills/`
- Se há um modelo base, estendê-lo — não recriar do zero
- Não adicionar código "por precaução" ou "para o futuro" — só o que a story pede

---

## 2. MULTI-TENANCY — REGRAS DE OURO

### 2.1 Nunca fazer queries sem contexto de tenant

```python
# ❌ PROIBIDO — query no schema errado
projects = Project.objects.all()

# ✅ CORRECTO — explícito e seguro
from django_tenants.utils import tenant_context
with tenant_context(tenant):
    projects = Project.objects.all()
```

### 2.2 Celery tasks — nunca passar objectos ORM

```python
# ❌ PROIBIDO — ORM object não é serializável cross-task
@app.task
def process_import(project):  # ← NUNCA
    ...

# ✅ CORRECTO — passar IDs primitivos + tenant_id
@app.task
def process_import(project_id: str, tenant_id: str):
    tenant = Client.objects.get(id=tenant_id)
    with tenant_context(tenant):
        project = Project.objects.get(id=project_id)
```

### 2.3 JWT — validar tenant em CADA request

```python
# Em IsTenantMember:
def has_permission(self, request, view):
    if not request.user.is_authenticated:
        return False
    # claim no token deve coincidir com schema activo
    token_schema = request.auth.payload.get('tenant_schema')
    active_schema = connection.schema_name
    return token_schema == active_schema
```

### 2.4 Testes de isolamento são OBRIGATÓRIOS

```
Antes de qualquer merge → pytest tests/tenant_isolation/ deve passar 100%
```

Testar sempre:
- User de tenant_a não vê dados de tenant_b
- JWT de tenant_a rejeitado em endpoint de tenant_b
- Celery task não contamina schema errado

---

## 3. SEGURANÇA

### 3.1 Secrets

```bash
# ❌ NUNCA no código
SECRET_KEY = "django-insecure-abc123"
IMO_CV_API_KEY = "live_key_xyz"

# ✅ SEMPRE em variáveis de ambiente
SECRET_KEY = os.environ['SECRET_KEY']
IMO_CV_API_KEY = os.environ.get('IMO_CV_API_KEY', '')
```

- `.env` nunca entra em git (está no `.gitignore`)
- `.env.example` documenta todas as variáveis sem valores reais

### 3.2 Autenticação e autorização

- Todos os endpoints requerem `IsAuthenticated` por default no `DEFAULT_PERMISSION_CLASSES`
- Endpoints públicos (ex: sitemap, webhook) devem ser explicitamente marcados com `AllowAny`
- Rate limiting obrigatório em todos os endpoints públicos: 100 req/hora por IP
- Nunca expor stack traces em produção (`DEBUG=False`, handler de erro customizado)

### 3.3 Uploads e media

```python
# Validar sempre: tipo de ficheiro, tamanho máximo, extensão
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']
MAX_UPLOAD_SIZE_MB = 10

# S3: usar presigned URLs — nunca servir via Django em produção
# Prefixo sempre por tenant: tenants/{slug}/...
```

### 3.4 SQL e injecção

- Nunca usar `raw()` ou `execute()` com strings formatadas pelo utilizador
- Usar sempre parâmetros parametrizados: `Model.objects.filter(name=user_input)`
- PostGIS: usar `GEOSGeometry` para validar input geográfico antes de guardar

---

## 4. QUALIDADE DE CÓDIGO

### 4.1 Antes de fazer commit

```bash
make lint          # black + flake8 + isort — deve passar sem erros
make test          # suite completa — coverage ≥80% nas apps core
pytest tests/tenant_isolation/  # SEMPRE — gate obrigatório
```

### 4.2 Type hints obrigatórios em código novo

```python
# ❌
def get_project(slug):
    ...

# ✅
def get_project(slug: str) -> Project | None:
    ...
```

### 4.3 Sem código morto

- Não deixar `print()`, `import pdb`, `breakpoint()`, comentários `TODO` sem issue associada
- Não deixar views/serializers comentados "para referência"
- Se removeres algo, remove completamente — não comentas

### 4.4 Modelos — regras estruturais

```python
# Todo o modelo de negócio DEVE ter:
id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)

# Modelos transaccionais DEVEM ter simple_history:
history = HistoricalRecords()
# (Project, Unit, Contract, Payment, Reservation)
```

---

## 5. OPERAÇÕES DESTRUTIVAS

### 5.1 Delete de tenant — protocolo obrigatório

```
NUNCA: Client.objects.filter(slug='x').delete()
NUNCA: DROP SCHEMA empresa_x CASCADE;

CORRECTO:
1. Soft delete: tenant.is_active = False; tenant.save()
2. Aguardar período de retenção (mínimo 30 dias)
3. Backup manual verificado
4. Drop manual por DBA com aprovação escrita do cliente
```

### 5.2 Migrations

```bash
# Antes de qualquer migration:
python manage.py migrate_schemas --shared    # Testar em shared
python manage.py migrate_schemas             # Testar em todos os tenants

# NUNCA fazer squash de migrations sem:
# - Ambiente de staging testado
# - Todos os schemas migrados com sucesso
# - Backup verificado
```

### 5.3 Git — operações proibidas sem aprovação explícita

```
❌ git push --force (em main ou develop)
❌ git reset --hard (com commits não publicados)
❌ Merge para main sem CI passing
❌ Merge para main sem code review aprovado
```

---

## 6. FRONTEND — REGRAS ESPECÍFICAS

### 6.1 JWT storage

```typescript
// ❌ NUNCA em localStorage — vulnerável a XSS
localStorage.setItem('token', jwt)

// ✅ SEMPRE em httpOnly cookie — gerido pelo servidor
// O refresh token nunca é acessível ao JavaScript
```

### 6.2 Tenant detection

```typescript
// Detectar tenant pelo subdomain — NUNCA por query param
const tenant = request.headers.host.split('.')[0]  // empresa-a

// metadataBase DEVE ser o subdomain completo
metadataBase: new URL(`https://${tenant.subdomain}.imos.cv`)
```

### 6.3 Dados sensíveis no cliente

- Nunca expor `imo_cv_api_key` ou `whatsapp_phone_id` no frontend
- Chamadas à API externa feitas sempre pelo backend
- Variáveis de ambiente Next.js: apenas `NEXT_PUBLIC_*` no cliente — verificar cada uma

---

## 7. MOBILE — REGRAS ESPECÍFICAS

### 7.1 Offline-first

```typescript
// Toda a escrita vai para WatermelonDB primeiro
// Sync com backend é assíncrono e resiliente a falha
// Nunca bloquear UI esperando resposta do servidor
```

### 7.2 Credenciais no dispositivo

```typescript
// ❌ AsyncStorage para tokens JWT (não encriptado)
// ✅ expo-secure-store ou react-native-keychain
```

---

## 8. CHECKLIST DE REVISÃO DE PR

Antes de aprovar qualquer PR, verificar:

- [ ] CI pipeline a verde (lint + tests + isolation)
- [ ] Coverage não diminuiu (≥80% nas apps core)
- [ ] Nenhum secret hardcoded
- [ ] Nenhuma query sem tenant_context (se código multi-tenant)
- [ ] Type hints presentes
- [ ] Sem código morto ou print statements
- [ ] Se novo modelo: tem UUID pk, created_at, updated_at
- [ ] Se modelo transaccional: tem simple_history
- [ ] Se novo endpoint: tem autenticação + permission class correcta
- [ ] Se Celery task: passa tenant_id como argumento primitivo
- [ ] Documentação da API actualizada (drf-spectacular) se endpoint novo/alterado

---

*Documento de referência para toda a equipa ImoOS | Sprint 1+*
