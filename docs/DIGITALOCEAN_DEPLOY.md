# 🚀 Guia de Deployment — DigitalOcean App Platform

**Data:** 2026-04-14  
**Status:** ✅ Documentado

---

## 📋 RESUMO EXECUTIVO

### ❓ Pergunta: Preciso rodar Docker Desktop antes de deploy para DigitalOcean?

**RESPOSTA: NÃO! ❌**

O DigitalOcean App Platform é **completamente independente** do seu Docker local.

---

## 🔄 COMPARAÇÃO DE AMBIENTES

### Local Development (Seu PC)

| Componente | Tecnologia | Onde roda |
|------------|-----------|-----------|
| Docker | Docker Desktop | Seu PC |
| PostgreSQL | Container Docker | Seu PC |
| Redis | Container Docker | Seu PC |
| Backend (Django) | Container Docker | Seu PC |
| Frontend (Next.js) | Container Docker | Seu PC |
| Setup | `setup-database.bat` | Seu PC |

**Precisa Docker Desktop?** ✅ **SIM**

**Quando usar:**
- Desenvolvimento de features
- Debug local
- Testes antes de commitar
- Desenvolvimento offline

---

### DigitalOcean Staging/Production

| Componente | Tecnologia | Onde roda |
|------------|-----------|-----------|
| App Platform | DO Managed | DigitalOcean Cloud |
| PostgreSQL | DO Managed Database | DigitalOcean Cloud |
| Redis/Valkey | DO Managed Cluster | DigitalOcean Cloud |
| Backend (Django) | DO Service | DigitalOcean Cloud |
| Frontend (Next.js) | DO Service | DigitalOcean Cloud |
| Setup | Pre-deploy job + API endpoint | DigitalOcean Cloud |

**Precisa Docker Desktop?** ❌ **NÃO**

**Quando usar:**
- Deploy para staging
- Deploy para produção
- Aplicação rodando para usuários reais
- **Tudo é automático via GitHub push**

---

## 🎯 WORKFLOW DIGITALOCEAN (Sem Docker Local)

### Fluxo Completo de Deploy

```
1. Você no PC:
   git push origin develop
   
2. GitHub:
   Recebe o push
   
3. DigitalOcean App Platform (AUTOMÁTICO):
   a. Detecta push para branch 'develop'
   b. Pull do código do GitHub
   c. Build das Docker images (no cloud da DO)
   d. Executa pre-deploy job "migrate":
      - migrate_schemas --shared
      - migrate_schemas --executor=parallel
      - ensure_public_tenant
   e. Deploy dos serviços:
      - API (Django/Gunicorn)
      - Frontend (Next.js)
      - Celery Worker
      - Celery Beat
   f. Health checks
   g. ✅ Aplicação online!
   
4. Você via browser:
   Criar superuser via API endpoint
   Criar tenants demo
   Testar login
```

**Tempo total:** ~5-10 minutos (automático)

**Docker Desktop necessário?** ❌ **NENHUM MOMENTO**

---

## 📦 O QUE O DIGITALOCEAN FORNECE

### Managed Services (Incluso no App Platform)

| Serviço | Tipo | Configuração |
|---------|------|--------------|
| **PostgreSQL** | Managed Database | PostgreSQL 15 + PostGIS |
| **Redis/Valkey** | Managed Cluster | Redis 7-compatible |
| **Object Storage** | DO Spaces | S3-compatible (fra1.digitaloceanspaces.com) |
| **App Platform** | PaaS | Containers gerenciados |
| **CDN** | DO CDN | Global (automático) |

### Infraestrutura Automática

✅ **Você NÃO precisa:**
- Instalar PostgreSQL
- Instalar Redis
- Configurar Docker
- Rodar migrations manualmente
- Gerenciar containers
- Configurar networking
- Gerenciar backups (DO faz automaticamente)

✅ **DigitalOcean faz automaticamente:**
- Provisiona banco de dados
- Provisiona Redis cluster
- Build das Docker images
- Executa migrations
- Deploy dos serviços
- Health checks
- Auto-scaling (configurável)
- Backups
- SSL/TLS
- Load balancing

---

## 🚀 COMO DEPLOYAR (Passo a Passo)

### Pré-requisitos

✅ **Você precisa ter:**
- Conta no DigitalOcean
- App Platform app criada (`imos-staging`)
- Repositório GitHub conectado ao DO
- Branch `develop` no GitHub

❌ **Você NÃO precisa:**
- Docker Desktop instalado
- Docker Desktop rodando
- Banco de dados local
- Redis local

### Passo 1: Push para GitHub

```bash
# No seu PC (sem Docker)
git add .
git commit -m "feat: minha feature"
git push origin develop
```

**Isto é tudo!** O resto é automático.

### Passo 2: DigitalOcean Detecta e Deploy (Automático)

O DO App Platform vai:

1. **Detectar push** para branch `develop`
2. **Build automático** das imagens Docker
3. **Executar pre-deploy job** (`migrate`):
   ```bash
   python manage.py migrate_schemas --shared
   python manage.py migrate_schemas --executor=parallel
   python manage.py ensure_public_tenant
   ```
4. **Deploy dos serviços:**
   - `api` — Django/Gunicorn (porta 8000)
   - `frontend` — Next.js (porta 3000)
   - `celery-worker` — Celery worker
   - `celery-beat` — Celery scheduler
5. **Health checks** — Verifica se API está saudável
6. ✅ **Aplicação online!**

### Passo 3: Verificar Deploy

**Via DigitalOcean Dashboard:**
1. Ir para: https://cloud.digitalocean.com/apps
2. Selecionar `imos-staging`
3. Ver status: "Active" ou "Deploying"
4. Clicar em "Live App" para abrir

**Via Console DO (opcional):**
```bash
# Usando doctl (DigitalOcean CLI)
doctl apps list
doctl apps get <app-id>
doctl apps logs <app-id> --follow
```

---

## 🔧 POST-DEPLOY: Criar Superuser e Dados

Após o deploy, a aplicação está rodando mas **sem superuser**.

### Opção 1: Via API Endpoint (Recomendado)

**Endpoint:** `POST /api/v1/setup/superuser/`

**Headers:**
```
Content-Type: application/json
X-Setup-Token: imos-setup-2026
```

**Body:**
```json
{
  "email": "admin@proptech.cv",
  "password": "ImoOS2026",
  "first_name": "Admin",
  "last_name": "ImoOS"
}
```

**Via curl:**
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

**Resposta (sucesso):**
```json
{
  "message": "Superuser created successfully",
  "email": "admin@proptech.cv"
}
```

**Verificar status:**
```bash
curl https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/status/
# Retorna: {"needs_setup": false, "has_superuser": true}
```

### Opção 2: Via DO Console (Management Command)

Se precisar rodar commands manualmente:

1. Ir para DO Dashboard → Apps → `imos-staging`
2. Clicar em "Console" (no serviço `api`)
3. Executar commands:

```bash
# Criar superuser
python manage.py create_platform_superadmin \
  --email=admin@proptech.cv \
  --password=ImoOS2026

# Criar tenant demo
python manage.py create_tenant \
  --schema=demo_promotora \
  --name="Demo Promotora" \
  --domain=demo.proptech.cv \
  --plan=pro

# Criar usuários demo
python manage.py ensure_demo_users --tenant=demo_promotora
```

---

## 🧪 TESTAR LOGIN APÓS DEPLOY

### Super Admin Login

**URL:** https://proptech.cv/superadmin/login

**Credenciais:**
- Email: `admin@proptech.cv`
- Senha: `ImoOS2026`

### Tenant Login

**URL:** https://demo.proptech.cv/login

**Credenciais:**
- Email: `gerente@demo.cv`
- Senha: `Demo2026!`

### Via API

**Testar superadmin:**
```bash
curl -X POST https://imos-staging-jiow3.ondigitalocean.app/api/v1/users/auth/superadmin/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@proptech.cv",
    "password": "ImoOS2026"
  }'
```

**Testar tenant:**
```bash
curl -X POST https://imos-staging-jiow3.ondigitalocean.app/api/v1/users/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "gerente@demo.cv",
    "password": "Demo2026!",
    "tenant_domain": "demo.proptech.cv"
  }'
```

---

## 🔍 TROUBLESHOOTING (DigitalOcean)

### Problema: Deploy falhou

**Verificar logs:**
1. DO Dashboard → Apps → `imos-staging`
2. Clicar em "Deployments"
3. Selecionar deploy falhado
4. Clicar em "View Logs"

**Erros comuns:**

**❌ "Migration failed"**
- Verificar se pre-deploy job está configurado corretamente
- Verificar logs do job `migrate`
- Pode precisar rodar migrations manualmente via console

**❌ "Database connection failed"**
- Verificar se banco de dados está provisionado
- Verificar env vars: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Verificar se `${db.HOSTNAME}` está correto no `imos-staging.yaml`

**❌ "Redis connection failed"**
- Verificar se cluster Redis está ativo
- Verificar env var: `REDIS_URL`
- Verificar se `${redis.DATABASE_URL}` está correto

### Problema: Login falha após deploy

**Diagnóstico:**

1. **Verificar se superuser existe:**
   ```bash
   curl https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/status/
   # Deve retornar: {"needs_setup": false, "has_superuser": true}
   ```

2. **Se needs_setup=true, criar superuser:**
   ```bash
   curl -X POST https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/superuser/ \
     -H "Content-Type: application/json" \
     -H "X-Setup-Token: imos-setup-2026" \
     -d '{"email":"admin@proptech.cv","password":"ImoOS2026","first_name":"Admin","last_name":"ImoOS"}'
   ```

3. **Verificar se tenant existe:**
   - Acessar DO Console do serviço `api`
   - Rodar:
     ```bash
     python manage.py shell_plus
     >>> from apps.tenants.models import Client
     >>> Client.objects.all()
     ```

4. **Verificar logs da API:**
   - DO Dashboard → Apps → `api` → Logs
   - Procurar por erros de autenticação

### Problema: "Tenant não encontrado"

**Causa:** Domain não registrado ou tenant não criado

**Solução via DO Console:**
```bash
python manage.py shell_plus

>>> from apps.tenants.models import Client, Domain
>>> from apps.tenants.management.commands.create_tenant import Command

# Criar tenant
cmd = Command()
cmd.handle(
    schema='demo_promotora',
    name='Demo Promotora',
    domain='demo.proptech.cv',
    plan='pro'
)
```

### Problema: "Credenciais inválidas" no staging

**Causas possíveis:**

1. **DEV_SKIP_AUTH ativo no staging** (deve estar `False`!)
   - Verificar `config/settings/staging.py`
   - **NÃO** deve ter `DEV_SKIP_AUTH = True`
   - Apenas `development.py` pode ter isso

2. **Usuário não existe no banco**
   - Criar via setup endpoint ou console

3. **Password hash errado**
   - Resetar password:
     ```bash
     python manage.py shell_plus
     >>> from apps.users.models import User
     >>> user = User.objects.get(email='admin@proptech.cv')
     >>> user.set_password('ImoOS2026')
     >>> user.save()
     ```

---

## 📊 CONFIGURAÇÃO ATUAL (imos-staging.yaml)

### Domains Configurados

| Domain | Tipo | URL |
|--------|------|-----|
| `imos-staging-jiow3.ondigitalocean.app` | PRIMARY | URL padrão DO |
| `proptech.cv` | ALIAS | Domínio customizado |
| `www.proptech.cv` | ALIAS | Domínio customizado |
| `demo.proptech.cv` | ALIAS | Tenant demo |

### Serviços

| Serviço | Tipo | Instância |
|---------|------|-----------|
| `api` | Service | professional-xs (porta 8000) |
| `frontend` | Service | professional-xs (porta 3000) |
| `celery-worker` | Worker | professional-xs |
| `celery-beat` | Worker | basic-xxs |
| `migrate` | Pre-deploy Job | apps-s-1vcpu-1gb |

### Pre-deploy Job (Migrations)

```yaml
jobs:
  - name: migrate
    kind: PRE_DEPLOY
    run_command: >
      bash -c '
        python manage.py migrate_schemas --shared &&
        python manage.py migrate_schemas --executor=parallel &&
        python manage.py ensure_public_tenant &&
        echo "Migrations completed. Use /api/v1/setup/superuser/ endpoint to create superuser"
      '
```

**O que faz:**
1. ✅ Migrações do schema público (shared apps)
2. ✅ Migrações de todos os tenants (parallel)
3. ✅ Garante que public tenant existe
4. ✅ Mensagem para criar superuser via API

---

## 🔐 SEGURANÇA (DigitalOcean)

### Secrets Gerenciados

Todos os secrets são **encrypted** no DO App Platform:

| Secret | Escopo | Uso |
|--------|--------|-----|
| `SECRET_KEY` | RUN_AND_BUILD_TIME | Django signing |
| `DB_PASSWORD` | RUN_AND_BUILD_TIME | Database access |
| `AWS_SECRET_ACCESS_KEY` | RUN_AND_BUILD_TIME | DO Spaces |
| `TWILIO_AUTH_TOKEN` | RUN_AND_BUILD_TIME | WhatsApp |
| `SETUP_SECRET_TOKEN` | RUN_AND_BUILD_TIME | Setup endpoint |

### Environment Variables

Configuradas no `imos-staging.yaml`:
- `DJANGO_SETTINGS_MODULE=config.settings.staging`
- `DEBUG=False`
- `ALLOWED_HOSTS=*`
- `CORS_ALLOWED_ORIGINS` (lista de domains)

### ⚠️ IMPORTANTE: DEV_SKIP_AUTH

**NUNCA** ativar `DEV_SKIP_AUTH` no staging/production!

**Verificar:**
```python
# config/settings/staging.py
# NÃO deve ter:
# DEV_SKIP_AUTH = True  ❌ ERRADO!

# Apenas em:
# config/settings/development.py
DEV_SKIP_AUTH = True  ✅ CORRETO (apenas local)
```

---

## 📝 CHECKLIST DE DEPLOY

### Antes do Push

- [ ] Código testado localmente (com Docker Desktop)
- [ ] Migrations criadas: `python manage.py makemigrations`
- [ ] Tests passando: `pytest`
- [ ] Lint passando: `make lint`
- [ ] **DEV_SKIP_AUTH** apenas em `development.py`
- [ ] Commits seguem padrão do projeto
- [ ] Push para branch `develop` (staging) ou `main` (production)

### Após Push (Automático)

- [ ] DO detecta push automaticamente
- [ ] Build inicia (~2-3 minutos)
- [ ] Pre-deploy job roda migrations (~1-2 minutos)
- [ ] Services deploy (~1-2 minutos)
- [ ] Health checks passam
- [ ] ✅ Status: "Active"

### Post-deploy (Manual)

- [ ] Verificar logs: DO Dashboard → Apps → Logs
- [ ] Testar health check: `https://<domain>/api/v1/health/`
- [ ] Criar superuser via API endpoint
- [ ] Verificar status: `/api/v1/setup/status/`
- [ ] Criar tenants demo (se necessário)
- [ ] Testar login: `/superadmin/login` e `/login`

---

## 🆚 COMPARAÇÃO FINAL

### Local Development (Docker Desktop)

```
Seu PC:
  ✅ Docker Desktop
  ✅ docker-compose.dev.yml
  ✅ setup-database.bat
  ✅ Banco local
  ✅ Redis local
  
Workflow:
  1. docker-compose up -d
  2. .\setup-database.bat
  3. http://localhost:8001/login
  
Quando usar:
  - Desenvolvimento
  - Debug
  - Testes locais
```

### DigitalOcean (Sem Docker Local)

```
DigitalOcean Cloud:
  ❌ Docker Desktop NÃO necessário
  ✅ DO App Platform
  ✅ DO Managed PostgreSQL
  ✅ DO Managed Redis
  ✅ DO Spaces (S3)
  
Workflow:
  1. git push origin develop
  2. DO faz deploy automático
  3. Criar superuser via API
  4. https://proptech.cv/login
  
Quando usar:
  - Staging
  - Production
  - Demo para clientes
```

---

## 🎯 RESUMO

### ❓ Preciso rodar Docker Desktop antes de deploy para DigitalOcean?

**RESPOSTA: NÃO! ❌**

**Razões:**
1. ✅ DO App Platform faz build das images automaticamente
2. ✅ DO provisiona banco de dados e Redis
3. ✅ DO executa migrations via pre-deploy job
4. ✅ DO deploya todos os serviços
5. ✅ Tudo é gerenciado e automático

**Workflow correto:**
```
Desenvolvimento local (com Docker Desktop)
  ↓
git push origin develop
  ↓
DigitalOcean faz deploy automático (SEM Docker local)
  ↓
Criar superuser via API endpoint
  ↓
✅ Aplicação online!
```

### 🚀 PRÓXIMO PASSO

**Se quer deployar para DigitalOcean AGORA:**

1. **Push para GitHub:**
   ```bash
   git push origin develop
   ```

2. **Aguardar deploy (~5-10 minutos)**

3. **Criar superuser:**
   ```bash
   curl -X POST https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/superuser/ \
     -H "Content-Type: application/json" \
     -H "X-Setup-Token: imos-setup-2026" \
     -d '{"email":"admin@proptech.cv","password":"ImoOS2026","first_name":"Admin","last_name":"ImoOS"}'
   ```

4. **Testar login:**
   - https://proptech.cv/superadmin/login
   - https://demo.proptech.cv/login

**Docker Desktop?** ❌ **NÃO PRECISA!**

---

*Última atualização: 2026-04-14*  
*Status: ✅ Documentado e pronto para deploy*
