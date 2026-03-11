# DevOps: GitHub + Staging Setup

## 1. Checklist Pré-Push

```bash
chmod +x scripts/pre_push_check.sh
./scripts/pre_push_check.sh
```

Verifica automaticamente:
- `.env` não está staged
- Sem secrets hardcoded no diff
- `DEBUG=True` apenas em dev/test
- `.gitignore` cobre `.env`
- Sem `print()` novos
- Formatação `black`

---

## 2. Criar Repositório GitHub

```bash
# Inicializar e fazer primeiro push
git init
git add .
git commit -m "feat: initial ImoOS project setup"
git branch -M main
git remote add origin git@github.com:your-org/imos.git
git push -u origin main

# Criar branch develop
git checkout -b develop
git push -u origin develop
```

### Branch Protection (GitHub UI ou CLI)

```bash
# Via gh CLI — proteger main e develop
gh api repos/your-org/imos/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["CI Gate (lint + test + isolation)"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \
  --field restrictions=null

gh api repos/your-org/imos/branches/develop/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["CI Gate (lint + test + isolation)"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \
  --field restrictions=null
```

---

## 3. DigitalOcean App Platform

### Pré-requisitos
```bash
# Instalar doctl
brew install doctl          # macOS
# ou: https://docs.digitalocean.com/reference/doctl/how-to/install/

doctl auth init             # autenticar com token DO
```

### Criar App
```bash
# Editar .do/app.yaml: substituir "your-org/imos" pelo teu repo

doctl apps create --spec .do/app.yaml
# Guarda o APP_ID retornado

# Ver estado
doctl apps list
doctl apps logs <APP_ID> --follow
```

### Secrets (App Platform env vars)
Adicionar via UI em App Platform → Settings → Environment Variables:

| Variável | Tipo |
|----------|------|
| `SECRET_KEY` | Secret |
| `DB_PASSWORD` | Secret (auto-preenchido se usar DB gerido DO) |
| `REDIS_URL` | Secret (auto-preenchido) |
| `AWS_ACCESS_KEY_ID` | Secret |
| `AWS_SECRET_ACCESS_KEY` | Secret |
| `SENTRY_DSN` | Secret |

---

## 4. GitHub Actions Secrets

Em GitHub → Settings → Secrets and variables → Actions:

| Secret | Valor |
|--------|-------|
| `DIGITALOCEAN_ACCESS_TOKEN` | Token DO com scope `app` |
| `DIGITALOCEAN_APP_ID` | ID da app (do `doctl apps list`) |
| `SENTRY_AUTH_TOKEN` | Token da Sentry org |
| `SENTRY_ORG` | Slug da org Sentry |
| `SENTRY_PROJECT` | Slug do projeto Sentry |

---

## 5. Sentry Setup

1. Criar projeto em sentry.io → Platform: Django
2. Copiar o DSN → adicionar como secret `SENTRY_DSN`
3. **LGPD**: `send_default_pii=False` já configurado em `staging.py`
4. A função `_scrub_sensitive_data` remove Authorization headers, cookies e query strings antes de envio

### Verificar que PII não é enviado
```bash
# Trigger um erro de teste e verificar no Sentry que:
# - Sem campo "user" no evento
# - Sem header "Authorization"
# - Sem query string
curl https://staging.imos.cv/api/v1/nonexistent/
```

---

## 6. Fluxo CD (automático)

```
git push origin develop
       ↓
GitHub Actions: ci.yml (lint + security + test + isolation)
       ↓ (se tudo verde)
GitHub Actions: deploy-staging.yml
       ↓
doctl apps create-deployment
       ↓
DO App Platform: release phase (migrate + collectstatic)
       ↓
Smoke test: GET /api/v1/health/ → 200
       ↓
Sentry release notificado
```

---

## 7. Verificação Final

```bash
# Health check
curl https://staging.imos.cv/api/v1/health/
# Esperado: {"status": "ok", "checks": {"db": "ok", "cache": "ok"}}

# Ver logs em tempo real
doctl apps logs <APP_ID> --follow --type=run

# Ver deployments
doctl apps list-deployments <APP_ID>
```
