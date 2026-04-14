# 🔧 SOLUÇÃO DIGITALOCEAN - Login Fix

**Data:** 2026-04-14  
**Objetivo:** Corrigir login no DigitalOcean AGORA

---

## 🎯 O QUE FAZER AGORA (3 passos)

### ❌ O que NÃO fazer:
- Não rodar Docker Desktop (não precisa para DO)
- Não modificar código local antes de testar
- Não fazer setup local primeiro

### ✅ O que FAZER:
1. Push para GitHub
2. Aguardar deploy automático
3. Criar superuser via API

---

## 📋 PASSO 1: PREPARAR CÓDIGO

### Verificar se DEV_SKIP_AUTH está SOMENTE em development.py

```bash
# No seu PC, verificar se staging NÃO tem bypass
grep -r "DEV_SKIP_AUTH" config/settings/staging.py
# Deve retornar NADA (vazio)

# Verificar se development.py tem bypass
grep -r "DEV_SKIP_AUTH" config/settings/development.py
# Deve retornar: DEV_SKIP_AUTH = True
```

**Se staging.py tem DEV_SKIP_AUTH, REMOVER:**
```bash
# Editar config/settings/staging.py
# Remover ou comentar: DEV_SKIP_AUTH = True
```

### Commit e Push

```bash
git add config/settings/staging.py
git commit -m "fix: ensure DEV_SKIP_AUTH not in staging settings"
git push origin develop
```

---

## 📋 PASSO 2: AGUARDAR DEPLOY AUTOMÁTICO

### Verificar Status do Deploy

**Via DigitalOcean Dashboard:**
1. https://cloud.digitalocean.com/apps
2. Clicar em `imos-staging`
3. Ver "Deployments" tab
4. Aguardar status: "Active"

**Tempo estimado:** 5-10 minutos

**O que acontece automaticamente:**
- ✅ Build das imagens Docker (no cloud DO)
- ✅ Pre-deploy job roda:
  ```bash
  python manage.py migrate_schemas --shared
  python manage.py migrate_schemas --executor=parallel
  python manage.py ensure_public_tenant
  ```
- ✅ Deploy dos serviços (API, Frontend, Celery)
- ✅ Health checks

---

## 📋 PASSO 3: CRIAR SUPERUSER E TESTAR

### Opção A: Via API Endpoint (Rápido)

**1. Verificar se precisa de setup:**
```bash
curl https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/status/
```

**Resposta esperada:**
```json
{"needs_setup": true, "has_superuser": false}
```

**2. Criar superuser:**
```bash
curl -X POST https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/superuser/ \
  -H "Content-Type: application/json" \
  -H "X-Setup-Token: imos-setup-2026" \
  -d '{
    "email": "admin@proptech.cv",
    "password": "ImoOS2026",
    "first_name": "Admin",
    "last_name": "ImoOS"
  }'
```

**Resposta de sucesso:**
```json
{
  "message": "Superuser created successfully",
  "email": "admin@proptech.cv"
}
```

**3. Verificar status novamente:**
```bash
curl https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/status/
# Deve retornar: {"needs_setup": false, "has_superuser": true}
```

### Opção B: Via DO Console (Se API não funcionar)

**1. Abrir Console no DO Dashboard:**
- https://cloud.digitalocean.com/apps
- `imos-staging` → Componente `api` → "Console"

**2. Rodar comando:**
```bash
python manage.py create_platform_superadmin \
  --email=admin@proptech.cv \
  --password=ImoOS2026
```

---

## 🧪 PASSO 4: TESTAR LOGIN

### Teste 1: Super Admin Login

**Via Browser:**
- URL: https://proptech.cv/superadmin/login
- Email: `admin@proptech.cv`
- Senha: `ImoOS2026`

**Via API:**
```bash
curl -X POST https://imos-staging-jiow3.ondigitalocean.app/api/v1/users/auth/superadmin/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@proptech.cv",
    "password": "ImoOS2026"
  }'
```

**Resposta esperada:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "tenant_schema": "public",
  "tenant_name": "Platform",
  "user": {
    "id": "uuid-aqui",
    "email": "admin@proptech.cv",
    "is_staff": true
  }
}
```

### Teste 2: Tenant Login (se tenant existe)

**Se tenant `demo_promotora` já existe:**
- URL: https://demo.proptech.cv/login
- Email: `gerente@demo.cv`
- Senha: `Demo2026!`

**Se tenant NÃO existe, criar via DO Console:**
```bash
python manage.py create_tenant \
  --schema=demo_promotora \
  --name="Demo Promotora" \
  --domain=demo.proptech.cv \
  --plan=pro

python manage.py ensure_demo_users --tenant=demo_promotora
```

---

## 🚨 TROUBLESHOOTING AGORA

### Problema: "Credenciais inválidas" após deploy

**Causa 1: Superuser não foi criado**
```bash
# Verificar
curl https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/status/

# Se needs_setup=true, criar:
curl -X POST https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/superuser/ \
  -H "X-Setup-Token: imos-setup-2026" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@proptech.cv","password":"ImoOS2026","first_name":"Admin","last_name":"ImoOS"}'
```

**Causa 2: DEV_SKIP_AUTH ativo no staging**
```bash
# Verificar via DO Console:
cat config/settings/staging.py | grep DEV_SKIP_AUTH
# Se encontrar, remover e fazer novo deploy
```

**Causa 3: Migrations não rodaram**
```bash
# Ver logs do pre-deploy job no DO Dashboard
# Se falhou, rodar manualmente via Console:
python manage.py migrate_schemas
```

### Problema: Deploy falhou

**Verificar logs:**
1. DO Dashboard → Apps → `imos-staging`
2. "Deployments" tab
3. Clicar no deploy falhado
4. "View Logs"

**Erros comuns:**

**Migration failed:**
```bash
# Via DO Console:
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
```

**Database connection failed:**
- Verificar se banco está ativo no DO Dashboard
- Verificar env vars no App Platform

**Build failed:**
- Verificar se código está correto no branch `develop`
- Verificar se `imos-staging.yaml` está válido

### Problema: "Tenant não encontrado" no login

**Criar tenant via DO Console:**
```bash
python manage.py shell_plus

>>> from apps.tenants.management.commands.create_tenant import Command
>>> cmd = Command()
>>> cmd.handle(
...     schema='demo_promotora',
...     name='Demo Promotora',
...     domain='demo.proptech.cv',
...     plan='pro'
... )

>>> # Criar usuários
>>> from apps.tenants.management.commands.ensure_demo_users import Command
>>> cmd = Command()
>>> cmd.handle(tenant='demo_promotora')
```

---

## ✅ CHECKLIST RÁPIDO

- [ ] Código commitado e push feito
- [ ] Deploy completou com sucesso (status "Active")
- [ ] Health check passa: https://.../api/v1/health/
- [ ] Setup status: `{"needs_setup": true}`
- [ ] Superuser criado via API
- [ ] Setup status: `{"needs_setup": false}`
- [ ] Login superadmin funciona
- [ ] (Opcional) Tenant demo criado
- [ ] (Opcional) Login tenant funciona

---

## 🎯 SCRIPT AUTOMÁTICO

Copie e execute este script no seu terminal (PowerShell):

```powershell
# ========================================
# ImoOS - DigitalOcean Deploy Script
# ========================================

Write-Host "🚀 Deploying to DigitalOcean..." -ForegroundColor Green

# Step 1: Commit and push
Write-Host "`n📦 Committing changes..." -ForegroundColor Yellow
git add .
git commit -m "deploy: fix auth for DigitalOcean"
git push origin develop

Write-Host "✅ Push completo!" -ForegroundColor Green
Write-Host "`n⏳ Aguardando deploy do DigitalOcean (5-10 minutos)..." -ForegroundColor Yellow
Write-Host "Verifique em: https://cloud.digitalocean.com/apps" -ForegroundColor Cyan

# Step 2: Wait for deployment
Write-Host "`n🔍 Verificando status do deploy..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 3: Create superuser
Write-Host "`n👤 Criando superuser..." -ForegroundColor Yellow
$superuserResponse = Invoke-RestMethod -Uri "https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/superuser/" `
  -Method POST `
  -Headers @{
    "Content-Type" = "application/json"
    "X-Setup-Token" = "imos-setup-2026"
  } `
  -Body (@{
    email = "admin@proptech.cv"
    password = "ImoOS2026"
    first_name = "Admin"
    last_name = "ImoOS"
  } | ConvertTo-Json)

Write-Host "✅ Superuser criado: $($superuserResponse.message)" -ForegroundColor Green

# Step 4: Test login
Write-Host "`n🧪 Testando login..." -ForegroundColor Yellow
$loginResponse = Invoke-RestMethod -Uri "https://imos-staging-jiow3.ondigitalocean.app/api/v1/users/auth/superadmin/token/" `
  -Method POST `
  -Headers @{
    "Content-Type" = "application/json"
  } `
  -Body (@{
    email = "admin@proptech.cv"
    password = "ImoOS2026"
  } | ConvertTo-Json)

Write-Host "✅ Login funciona!" -ForegroundColor Green
Write-Host "📧 Email: $($loginResponse.user.email)" -ForegroundColor Cyan
Write-Host "🔑 Token recebido: $($loginResponse.access.Substring(0, 20))..." -ForegroundColor Cyan

Write-Host "`n🎉 Deploy completo!" -ForegroundColor Green
Write-Host "🌐 Super Admin: https://proptech.cv/superadmin/login" -ForegroundColor Cyan
Write-Host "🌐 Tenant: https://demo.proptech.cv/login" -ForegroundColor Cyan
```

**Executar:**
```powershell
.\deploy-digitalocean.ps1
```

---

## 📞 SUPORTE RÁPIDO

Se algo não funcionar:

1. **Verificar logs:** DO Dashboard → Apps → Logs
2. **Verificar health:** `curl https://.../api/v1/health/`
3. **Verificar migrations:** DO Console → `python manage.py showmigrations`
4. **Reset deploy:** DO Dashboard → Apps → "Deploy" button

---

*Última atualização: 2026-04-14*  
*Status: ✅ Pronto para deploy*
