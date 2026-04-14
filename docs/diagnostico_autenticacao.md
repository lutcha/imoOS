# 🔍 DIAGNÓSTICO DE AUTENTICAÇÃO - ImoOS

## 📊 ESTADO ATUAL

### Problema Identificado
Ambos os logins falham com "Credenciais inválidas":
1. **Super Admin** (proptech.cv/superadmin/login) - admin@proptech.cv / ImoOS2026
2. **Tenant** (proptech.cv/login) - gerente@demo.cv / Demo2026!

---

## ✅ O QUE FUNCIONA (Infraestrutura Intacta)

### 1. Sistema de Autenticação Django/DRF
- ✅ **User Model** (`apps/users/models.py`) - Custom user com email-based auth
- ✅ **JWT Configuration** (`SIMPLE_JWT` in settings) - Access token 15min, Refresh token 7 dias
- ✅ **Authentication Backends** - ModelBackend + ObjectPermissionBackend
- ✅ **JWT Serializer** (`TenantTokenObtainPairSerializer`) - Injeta tenant claims no token
- ✅ **Views de Login** - `TenantTokenObtainPairView` e `SuperAdminTokenObtainPairView`
- ✅ **URLs configuradas** - `/api/v1/users/auth/token/` e `/api/v1/users/auth/superadmin/token/`

### 2. Tenant Middleware
- ✅ **ImoOSTenantMiddleware** - Roteia schemas baseado em Host header
- ✅ **JWT Fallback** - Extrai tenant do JWT quando Host falha (dev localhost)
- ✅ **Bypass paths** - Superadmin endpoints rodam em schema público

### 3. Permissões
- ✅ **IsTenantMember** - Valida tenant_schema claim vs schema ativo
- ✅ **IsTenantAdmin** - Verifica TenantMembership no schema do tenant
- ✅ **Superadmin check** - Valida `is_staff=True` explicitamente

### 4. Frontend Next.js
- ✅ **API Routes** - Proxies para Django (`/api/auth/login`, `/api/auth/superadmin-login`)
- ✅ **AuthContext** - Gerencia estado de autenticação
- ✅ **Token Storage** - Access token em memória, refresh token em httpOnly cookie
- ✅ **Middleware** - Proteção de rotas (tenant auth bypass para testes)

### 5. Comandos de Setup
- ✅ **create_superuser_public.py** - Cria admin@proptech.cv / ImoOS2026 no schema público
- ✅ **ensure_demo_users.py** - Cria gerente@demo.cv / Demo2026! no tenant demo_promotora
- ✅ **ensure_demo_tenant.py** - Cria tenant demo_promotora
- ✅ **create_platform_superadmin.py** - Alternativa para criar superadmin

---

## ❌ CAÍZAS PROVÁVEIS DO PROBLEMA

### Root Cause #1: Banco de Dados Não Inicializado
**Evidência:**
- Docker não está rodando (verificado: `docker ps` falhou)
- Sem `.env` local configurado para `db` host (usa `db` que só existe no Docker network)
- Users não existem no banco porque migrations/setup não foram executados

**Impacto:**
- Users `admin@proptech.cv` e `gerente@demo.cv` **NÃO EXISTEM** no banco de dados
- Tenant `demo_promotora` **NÃO EXISTE** no banco de dados
- Todas as migrations **NÃO FORAM APLICADAS**

### Root Cause #2: Domain/Tenant Mismatch
**Problema Potencial:**
- Frontend acessa `proptech.cv`
- Tenant demo pode ter domain `demo.proptech.cv` ou `demo.localhost`
- Middleware pode não conseguir resolver tenant correto

### Root Cause #3: JWT Blacklist Bug (Menor)
- `BLACKLIST_AFTER_ROTATION: True` mas app `token_blacklist` não está em INSTALLED_APPS
- Logout não funciona, mas login deveria funcionar

---

## 🎯 SOLUÇÃO EM 2 FASES

###  IMPORTANTE: DigitalOcean vs Local Development

**⚠️ ATENÇÃO: São ambientes DIFERENTES!**

| Ambiente | Onde roda | Database | Redis | Docker Local? |
|----------|-----------|----------|-------|---------------|
| **Local Development** | Seu PC (Docker Desktop) | PostgreSQL local | Redis local | ✅ **PRECISA** |
| **DigitalOcean Staging/Production** | DO App Platform | Managed PostgreSQL | Managed Redis | ❌ **NÃO PRECISA** |

**Para DigitalOcean:**
- ❌ **NÃO** precisa ter Docker Desktop rodando
- ❌ **NÃO** precisa fazer setup local primeiro
- ✅ Push para GitHub → DO faz deploy automático
- ✅ DO tem banco de dados e Redis gerenciados
- ✅ Migrations rodam automaticamente no deploy

**Para Desenvolvimento Local:**
- ✅ **PRECISA** Docker Desktop rodando
- ✅ Setup com `setup-database.bat` para testar localmente
- ✅ Útil para desenvolvimento e debug

---

### FASE 1: ACESSO IMEDIATO (Desenvolvimento Local)

#### Opção A: Bypass de Autenticação Temporário ⚡ RECOMENDADO

**Backend - Desativar validação de senha em desenvolvimento:**

```python
# config/settings/development.py
# ADICIONAR no final do arquivo:

# ⚠️ TEMPORÁRIO: Bypass de autenticação para desenvolvimento
# REMOVER antes de commitar para produção!
DEV_SKIP_AUTH = True
```

```python
# apps/users/views.py - Modificar TenantTokenObtainPairView

from django.conf import settings

class TenantTokenObtainPairView(TokenObtainPairView):
    serializer_class = TenantTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # ⚠️ DEV BYPASS - Remover em produção
        if getattr(settings, 'DEV_SKIP_AUTH', False):
            return self._dev_bypass_login(request)
        return super().post(request, *args, **kwargs)
    
    def _dev_bypass_login(self, request):
        """Retorna token válido sem validar credenciais (APENAS DEV)"""
        from django.db import connection
        from apps.tenants.models import Client
        
        # Usar tenant demo ou resolver pelo tenant_domain
        tenant_domain = request.data.get('tenant_domain', 'demo.proptech.cv')
        
        try:
            domain = Domain.objects.get(domain=tenant_domain)
            tenant = domain.tenant
            connection.set_tenant(tenant)
        except Domain.DoesNotExist:
            # Fallback: usar primeiro tenant ativo
            tenant = Client.objects.filter(is_active=True).first()
            if not tenant:
                return Response(
                    {'detail': 'Nenhum tenant configurado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            connection.set_tenant(tenant)
        
        # Pegar primeiro usuário ativo do tenant (admin se possível)
        from apps.users.models import User
        user = User.objects.filter(is_active=True).order_by('-is_staff').first()
        
        if not user:
            return Response(
                {'detail': 'Nenhum usuário disponível'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Gerar token sem validar senha
        refresh = self.serializer_class.get_token(user)
        data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'tenant_schema': connection.schema_name,
            'tenant_name': tenant.name,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': user.role,
                'is_staff': user.is_staff,
            }
        }
        return Response(data, status=status.HTTP_200_OK)
```

**Aplicar o mesmo para SuperAdminTokenObtainPairView:**

```python
class SuperAdminTokenObtainPairView(TokenObtainPairView):
    serializer_class = TenantTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # ⚠️ DEV BYPASS
        if getattr(settings, 'DEV_SKIP_AUTH', False):
            return self._dev_bypass_superadmin_login(request)
        return super().post(request, *args, **kwargs)
    
    def _dev_bypass_superadmin_login(self, request):
        """Retorna token de superadmin sem validar credenciais (APENAS DEV)"""
        from django.db import connection
        connection.set_schema_to_public()
        
        from apps.users.models import User
        # Pegar primeiro superuser ou criar um
        user = User.objects.filter(is_staff=True, is_active=True).first()
        
        if not user:
            # Criar superuser temporário
            user = User.objects.create_superuser(
                email='dev@proptech.cv',
                password='dev',
                first_name='Dev',
                last_name='Admin'
            )
        
        refresh = self.serializer_class.get_token(user)
        data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'tenant_schema': 'public',
            'tenant_name': 'Platform',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': user.role,
                'is_staff': True,
            }
        }
        return Response(data, status=status.HTTP_200_OK)
```

---

### FASE 2: CORREÇÃO PERMANENTE

#### Passo 1: Inicializar Banco de Dados Corretamente

```bash
# 1. Iniciar Docker
docker-compose -f docker-compose.dev.yml up -d

# 2. Aguardar serviços ficarem saudáveis
docker-compose -f docker-compose.dev.yml ps

# 3. Executar migrations
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate_schemas

# 4. Criar tenant demo
docker-compose -f docker-compose.dev.yml exec web python manage.py create_tenant \
  --schema=demo_promotora \
  --name="Demo Promotora" \
  --domain=demo.proptech.cv \
  --plan=pro

# 5. Criar superuser no schema público
docker-compose -f docker-compose.dev.yml exec web python manage.py create_superuser_public

# 6. Criar usuários demo no tenant
docker-compose -f docker-compose.dev.yml exec web python manage.py ensure_demo_users \
  --tenant=demo_promotora
```

#### Passo 2: Verificar Estado

```bash
# Verificar se usuários existem
docker-compose -f docker-compose.dev.yml exec web python manage.py shell_plus

>>> from django.db import connection
>>> from apps.users.models import User

# Verificar superadmin (schema público)
>>> connection.set_schema_to_public()
>>> User.objects.filter(is_staff=True)
<QuerySet [<User: admin@proptech.cv>]>

# Verificar usuários do tenant demo
>>> from apps.tenants.models import Client
>>> tenant = Client.objects.get(schema_name='demo_promotora')
>>> connection.set_tenant(tenant)
>>> User.objects.all()
<QuerySet [
  <User: admin@demo.cv>,
  <User: gerente@demo.cv>,
  <User: vendas@demo.cv>,
  ...
]>
```

#### Passo 3: Configurar Domínio Corretamente

**Problema:** Frontend acessa `proptech.cv` mas tenant pode ter domain `demo.proptech.cv`

**Solução:** Criar domain alias ou usar domain correto

```python
# Opção 1: Criar domain sem subdomínio
>>> from apps.tenants.models import Domain
>>> Domain.objects.create(
...     tenant=tenant,
...     domain='proptech.cv',
...     is_primary=True
... )

# Opção 2: Acessar com subdomínio correto
# http://demo.proptech.cv/login
```

#### Passo 3: Testar Login via API

```bash
# Testar login tenant
curl -X POST http://localhost:8001/api/v1/users/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "gerente@demo.cv",
    "password": "Demo2026!",
    "tenant_domain": "demo.proptech.cv"
  }'

# Testar login superadmin
curl -X POST http://localhost:8001/api/v1/users/auth/superadmin/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@proptech.cv",
    "password": "ImoOS2026"
  }'
```

---

## 🔧 CHECKLIST DE IMPLEMENTAÇÃO

### Imediato (FASE 1):
- [ ] Adicionar `DEV_SKIP_AUTH = True` em `config/settings/development.py`
- [ ] Modificar `TenantTokenObtainPairView` com bypass
- [ ] Modificar `SuperAdminTokenObtainPairView` com bypass
- [ ] Testar login no frontend
- [ ] Adicionar aviso visual "DEV MODE" no frontend

### Permanente (FASE 2):
- [ ] Iniciar Docker services
- [ ] Executar `migrate_schemas`
- [ ] Criar tenant `demo_promotora` com domain correto
- [ ] Executar `create_superuser_public`
- [ ] Executar `ensure_demo_users --tenant=demo_promotora`
- [ ] Verificar domains no banco
- [ ] Testar login via API
- [ ] Remover código de bypass DEV
- [ ] Documentar setup correto no README

---

## 📝 NOTAS IMPORTANTES

### Segurança
- ⚠️ **NUNCA** commitar código de bypass para branches `main` ou `develop`
- ⚠️ **SEMPRE** remover `DEV_SKIP_AUTH` antes de deploy
- ⚠️ Usar apenas em `development.py`, nunca em `production.py`

### Multi-Tenant
- ✅ Superadmin vive no schema `public`
- ✅ Usuários tenant vivem no schema do tenant (ex: `demo_promotora`)
- ✅ JWT deve conter claim `tenant_schema` correto
- ✅ Middleware deve resolver tenant antes de autenticar

### Domains
- Tenant precisa de registro na tabela `Domain`
- Domain deve corresponder ao Host header ou `tenant_domain` no body
- Localhost dev pode precisar de configuração especial

---

## 🚀 COMANDOS RÁPIDOS DE VERIFICAÇÃO

```bash
# 1. Ver se Docker está rodando
docker ps

# 2. Ver logs do backend
docker-compose -f docker-compose.dev.yml logs -f web

# 3. Acessar Django shell
docker-compose -f docker-compose.dev.yml exec web python manage.py shell_plus

# 4. Ver tenants
docker-compose -f docker-compose.dev.yml exec web python manage.py shell_plus
>>> from apps.tenants.models import Client
>>> Client.objects.all()

# 5. Ver domains
>>> from apps.tenants.models import Domain
>>> Domain.objects.all()

# 6. Ver users (public schema)
>>> from django.db import connection
>>> connection.set_schema_to_public()
>>> from apps.users.models import User
>>> User.objects.all()

# 7. Ver users (tenant schema)
>>> tenant = Client.objects.get(schema_name='demo_promotora')
>>> connection.set_tenant(tenant)
>>> User.objects.all()

# 8. Testar auth manualmente
>>> from django.contrib.auth import authenticate
>>> user = authenticate(email='admin@proptech.cv', password='ImoOS2026')
>>> user
```

---

## 📞 PRÓXIMOS PASSOS

1. **Iniciar Docker** - Serviços precisam estar rodando
2. **Verificar estado do banco** - Rode os comandos acima para diagnosticar
3. **Executar setup** - Migrations + create tenant + create users
4. **Opcional: Bypass DEV** - Se precisar de acesso imediato antes do setup completo
5. **Testar login** - Via API primeiro, depois frontend
6. **Documentar** - Atualizar README com passos de setup

---

*Gerado em 2026-04-14*
*Status: Aguardando execução*
