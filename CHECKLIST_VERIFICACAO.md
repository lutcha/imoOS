# ✅ CHECKLIST DE VERIFICAÇÃO - Login Fix

**Data:** 2026-04-14  
**Status:** ⏳ Aguardando execução

---

## 📋 PRE-REQUISITOS

- [ ] Docker Desktop instalado
- [ ] Docker Desktop rodando (ícone verde na taskbar)
- [ ] Terminal aberto em `c:\Dev\imos`
- [ ] Conexão com internet (para baixar images Docker se necessário)

---

## 🔍 VERIFICAÇÃO DE ARQUIVOS

### Arquivos Modificados (3):

- [ ] `config/settings/development.py` - Contém `DEV_SKIP_AUTH = True`
- [ ] `apps/users/views.py` - Contém methods `_dev_bypass_login` e `_dev_bypass_superadmin_login`
- [ ] `frontend/src/app/(auth)/layout.tsx` - Contém banner de DEV mode

### Arquivos Criados (7):

- [ ] `setup-database.bat` - Script Windows
- [ ] `setup-database.sh` - Script Linux/Mac
- [ ] `docs/diagnostico_autenticacao.md` - Diagnóstico técnico
- [ ] `docs/SOLUCAO_LOGIN.md` - Guia completo
- [ ] `.git-hooks/pre-commit` - Hook de segurança
- [ ] `RESUMO_EXECUTIVO.md` - Resumo executivo
- [ ] `QUICK_START.txt` - Quick start guide

### Verificação Visual:

```bash
# Verificar se DEV_SKIP_AUTH está no settings
findstr /C:"DEV_SKIP_AUTH = True" config\settings\development.py

# Verificar se bypass methods estão nas views
findstr /C:"_dev_bypass_login" apps\users\views.py
findstr /C:"_dev_bypass_superadmin_login" apps\users\views.py

# Verificar se banner está no layout
findstr /C:"MODO DESENVOLVIMENTO" frontend\src\app\(auth)\layout.tsx
```

---

## 🚀 EXECUÇÃO DO SETUP

### Passo 1: Verificar Docker

```bash
docker --version
docker ps
```

**Esperado:**
- Docker version 20.x ou superior
- Lista de containers (pode estar vazia)

- [ ] Docker versão verificada
- [ ] Docker rodando

### Passo 2: Executar Setup

```bash
.\setup-database.bat
```

**Verificar durante execução:**
- [ ] Mensagem "[1/6] Checking Docker..." aparece
- [ ] Mensagem "✓ Docker is running" aparece
- [ ] Mensagem "[2/6] Starting services..." aparece
- [ ] Containers iniciam (web, db, redis, celery, frontend)
- [ ] Mensagem "[3/6] Waiting for database..." aparece
- [ ] Mensagem "[4/6] Running database migrations..." aparece
- [ ] Migrations completam sem erro
- [ ] Mensagem "[5/6] Creating demo tenant..." aparece
- [ ] Tenant criado (ou mensagem de warning se já existir)
- [ ] Mensagem "[6/6] Creating users..." aparece
- [ ] Superuser criado: admin@proptech.cv
- [ ] Demo users criados: gerente@demo.cv, etc.
- [ ] Mensagem "✅ Setup Complete!" aparece

### Passo 3: Verificar Serviços

```bash
docker-compose -f docker-compose.dev.yml ps
```

**Esperado:**
- [ ] `imos_db_1` - status: Up (healthy)
- [ ] `imos_redis_1` - status: Up (healthy)
- [ ] `imos_web_1` - status: Up
- [ ] `imos_celery_1` - status: Up
- [ ] `imos_celery-beat_1` - status: Up
- [ ] `imos_frontend_1` - status: Up

### Passo 4: Verificar Logs

```bash
docker-compose -f docker-compose.dev.yml logs web | findstr "DEV_SKIP"
```

**Esperado:**
- [ ] Ver warning: "⚠️ DEV_SKIP_AUTH is enabled - authentication bypassed!"

---

## 🧪 TESTE DE LOGIN

### Teste 1: Super Admin Login

**Via Browser:**
1. Abrir: http://localhost:8001/superadmin/login
2. Verificar banner amarelo no topo
3. Inserir credenciais:
   - Email: `admin@proptech.cv`
   - Senha: `ImoOS2026`
4. Clicar "Entrar no Backoffice"

**Resultado esperado:**
- [ ] Login realizado com sucesso
- [ ] Redirecionado para dashboard superadmin
- [ ] JWT token recebido (verificar Network tab no DevTools)

**Via API (curl):**
```bash
curl -X POST http://localhost:8001/api/v1/users/auth/superadmin/token/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@proptech.cv\",\"password\":\"ImoOS2026\"}"
```

**Resultado esperado:**
- [ ] HTTP 200 OK
- [ ] JSON com campos: access, refresh, tenant_schema, tenant_name, user
- [ ] tenant_schema = "public"

### Teste 2: Tenant Login

**Via Browser:**
1. Abrir: http://localhost:8001/login
2. Verificar banner amarelo no topo
3. Inserir credenciais:
   - Email: `gerente@demo.cv`
   - Senha: `Demo2026!`
4. Clicar "Entrar"

**Resultado esperado:**
- [ ] Login realizado com sucesso
- [ ] Redirecionado para dashboard tenant
- [ ] JWT token recebido com tenant_schema="demo_promotora"

**Via API (curl):**
```bash
curl -X POST http://localhost:8001/api/v1/users/auth/token/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"gerente@demo.cv\",\"password\":\"Demo2026!\",\"tenant_domain\":\"demo.proptech.cv\"}"
```

**Resultado esperado:**
- [ ] HTTP 200 OK
- [ ] JSON com campos: access, refresh, tenant_schema, tenant_name, user
- [ ] tenant_schema = "demo_promotora"

### Teste 3: Bypass DEV (Credenciais Aleatórias)

**Via Browser:**
1. Abrir: http://localhost:8001/login
2. Inserir credenciais aleatórias:
   - Email: `qualquer@coisa.cv`
   - Senha: `qualquersenha`
3. Clicar "Entrar"

**Resultado esperado:**
- [ ] Login realizado com sucesso (bypass ativo)
- [ ] Usa primeiro usuário disponível no tenant

---

## 🔍 VERIFICAÇÃO DO BANCO DE DADOS

### Django Shell

```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py shell_plus
```

**Verificar tenants:**
```python
from apps.tenants.models import Client
Client.objects.all()
```
- [ ] Mostra: `demo_promotora`

**Verificar domains:**
```python
from apps.tenants.models import Domain
Domain.objects.all()
```
- [ ] Mostra: `demo.proptech.cv`

**Verificar superadmin:**
```python
from django.db import connection
connection.set_schema_to_public()
from apps.users.models import User
User.objects.filter(is_staff=True)
```
- [ ] Mostra: `admin@proptech.cv`

**Verificar usuários demo:**
```python
from apps.tenants.models import Client
tenant = Client.objects.get(schema_name='demo_promotora')
connection.set_tenant(tenant)
from apps.users.models import User
User.objects.all()
```
- [ ] Mostra: 6 usuários (admin, gerente, vendas, obra, cliente1, cliente2)

---

## 🎯 CHECKLIST FINAL

### Funcionalidade:
- [ ] ✅ Docker services rodando
- [ ] ✅ Migrations aplicadas
- [ ] ✅ Tenant demo_promotora existe
- [ ] ✅ Superadmin login funciona
- [ ] ✅ Tenant login funciona
- [ ] ✅ Bypass DEV ativo
- [ ] ✅ Banner amarelo visível

### Segurança:
- [ ] ✅ DEV_SKIP_AUTH apenas em development.py
- [ ] ✅ Pre-commit hook criado
- [ ] ⚠️ Pre-commit hook instalado (opcional)

### Documentação:
- [ ] ✅ SOLUCAO_LOGIN.md criada
- [ ] ✅ diagnostico_autenticacao.md criada
- [ ] ✅ RESUMO_EXECUTIVO.md criado
- [ ] ✅ QUICK_START.txt criado

---

## 📊 STATUS REPORT

**Data/Hora:** _______________  
**Executado por:** _______________  

**Resultados:**
- [ ] ✅ Tudo funcionando
- [ ] ⚠️ Funcionando com ressalvas: _______________
- [ ] ❌ Problemas encontrados: _______________

**Próximas ações:**
- [ ] Desativar DEV_SKIP_AUTH (quando pronto para produção)
- [ ] Instalar pre-commit hook: `copy .git-hooks\pre-commit .git\hooks\pre-commit`
- [ ] Atualizar README principal do projeto
- [ ] Commit mudanças (SEM DEV_SKIP_AUTH = True)

---

*Checklist criado em 2026-04-14*
