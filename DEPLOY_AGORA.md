# 🚀 DEPLOY DIGITALOCEAN - EXECUTE AGORA

## ⚡ RESPOSTA RÁPIDA

### ❓ Preciso Docker Desktop?
**NÃO!** DigitalOcean faz tudo automático.

### ❓ O que fazer agora?
**3 passos:**
1. `git push origin develop`
2. Aguardar 5-10 min
3. Criar superuser via API

---

## 📋 PASSO A PASSO COMPLETO

### ✅ VERIFICAÇÃO PRÉ-DEPLOY

**1. Verificar se staging está limpo (SEM bypass):**
```bash
# Deve retornar NADA
grep "DEV_SKIP_AUTH" config/settings/staging.py
```

**Resultado:** ✅ Limpo! Staging não tem `DEV_SKIP_AUTH`

**2. Verificar branch:**
```bash
git branch
# Deve mostrar: * develop (ou main para produção)
```

---

### 🚀 EXECUTAR DEPLOY

**Opção 1: Script Automático (Recomendado)**

```powershell
# No terminal PowerShell
.\deploy-digitalocean.ps1
```

O script vai:
- ✅ Fazer git push
- ✅ Aguardar deploy
- ✅ Criar superuser automaticamente
- ✅ Testar login
- ✅ Mostrar URLs

**Opção 2: Manual**

```bash
# 1. Push
git add .
git commit -m "deploy: fix auth for DigitalOcean"
git push origin develop

# 2. Aguardar 5-10 min
# Ver status: https://cloud.digitalocean.com/apps

# 3. Criar superuser
curl -X POST https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/superuser/ \
  -H "Content-Type: application/json" \
  -H "X-Setup-Token: imos-setup-2026" \
  -d '{
    "email": "admin@proptech.cv",
    "password": "ImoOS2026",
    "first_name": "Admin",
    "last_name": "ImoOS"
  }'

# 4. Testar login
curl -X POST https://imos-staging-jiow3.ondigitalocean.app/api/v1/users/auth/superadmin/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@proptech.cv","password":"ImoOS2026"}'
```

---

## 🔍 MONITORAR DEPLOY

**Via Dashboard:**
1. https://cloud.digitalocean.com/apps
2. Clicar em `imos-staging`
3. Ver "Deployments" tab
4. Aguardar: **Active** (verde)

**O que acontece:**
```
✅ Build images (2-3 min)
✅ Pre-deploy job - migrations (1-2 min)
✅ Deploy services (1-2 min)
✅ Health checks (30s)
✅ Total: ~5-10 minutos
```

---

## 🧪 TESTAR APÓS DEPLOY

**1. Health check:**
```bash
curl https://imos-staging-jiow3.ondigitalocean.app/api/v1/health/
# Deve retornar: {"status": "healthy"}
```

**2. Setup status:**
```bash
curl https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/status/
# Deve retornar: {"needs_setup": true/false, "has_superuser": true/false}
```

**3. Login superadmin:**
- URL: https://proptech.cv/superadmin/login
- Email: `admin@proptech.cv`
- Senha: `ImoOS2026`

**4. Login tenant (se existir):**
- URL: https://demo.proptech.cv/login
- Email: `gerente@demo.cv`
- Senha: `Demo2026!`

---

## 🚨 SE ALGO DER ERRADO

### Deploy falhou
- Ver logs: DO Dashboard → Apps → Logs
- Erro comum: migrations → rodar via Console DO

### Login falha
- Verificar se superuser foi criado:
  ```bash
  curl https://imos-staging-jiow3.ondigitalocean.app/api/v1/setup/status/
  ```
- Se `needs_setup: true`, criar superuser (ver passo 3 acima)

### "Tenant não encontrado"
- Criar tenant via DO Console:
  ```bash
  python manage.py create_tenant \
    --schema=demo_promotora \
    --name="Demo Promotora" \
    --domain=demo.proptech.cv \
    --plan=pro
  ```

---

## 📚 DOCUMENTAÇÃO COMPLETA

- `docs/SOLUCAO_DIGITALOCEAN_AGORA.md` - Guia completo + troubleshooting
- `docs/DIGITALOCEAN_DEPLOY.md` - Explicação detalhada DO vs Local
- `DOCKER_VS_DIGITALOCEAN.md` - Comparação rápida

---

## ✅ CHECKLIST FINAL

- [ ] Staging settings limpas (SEM DEV_SKIP_AUTH) ✅
- [ ] Código commitado
- [ ] Push para `develop`
- [ ] Deploy completo (status: Active)
- [ ] Superuser criado
- [ ] Login funciona
- [ ] 🎉 Pronto!

---

**PRÓXIMA AÇÃO:** Executar `.\deploy-digitalocean.ps1`

*2026-04-14*
