# Sprint 8 — Release 1.0 Cabo Verde

**Período:** Semana 20–23 (Go-Live Cabo Verde)
**Data de criação:** 18 Mar 2026
**Estado Sprint 7:** 100% COMPLETO

## Contexto — Sprint 8 = Estabilização + Release

Sprints 1–7 completaram toda a funcionalidade de negócio + infraestrutura de produção.
O Sprint 8 foca-se em:
1. **Estabilizar o login** (bug crítico: Turbopack + TENANT_DOMAIN host header)
2. **CI/CD pipeline** funcional para deploy automático na DigitalOcean
3. **Dados reais** — seed com promotoras piloto de Cabo Verde
4. **Mobile polishing** — React Native app pronta para TestFlight/Play Store
5. **Integração imo.cv** — publicar unidades automaticamente no marketplace
6. **Testes de carga** — validar performance antes do go-live

## Issues conhecidos a resolver ANTES do Sprint 8

### 🔴 Crítico: Login via Docker Turbopack
- **Problema**: Next.js 16 Turbopack (Docker) retorna 404 para `/api/auth/login`
- **Root cause**: Cache corrompido + `TENANT_DOMAIN` env var não propagado
- **Workaround actual**: `npm run dev -p 3002` (local, Webpack)
- **Fix permanente**: Prompt 00 deste sprint

### 🟠 Médio: Serializer `total_area` em Projects
- **Problema**: `ProjectSerializer` tem campo `total_area` que não existe no modelo
- **Fix**: Prompt 00 — remover campo do serializer

### 🟡 Menor: Dashboard stats 404 sem `/api/v1/dashboard/`
- **Fix**: verificar URL registration em `config/urls.py`

## Ordem de execução

| # | Ficheiro | Agente(s) | Prioridade |
|---|----------|-----------|------------|
| 00 | `00-bugfix-login-serializers.md` | `drf-viewset-builder`, `nextjs-tenant-routing` | 🔴 Crítico pré-release |
| 01 | `01-cicd-digitalocean.md` | `migration-orchestrator` | 🔴 Release blocker |
| 02 | `02-seed-data-caboverde.md` | `django-tenants-specialist` | 🟠 Alta |
| 03 | `03-mobile-release-prep.md` | `react-component-builder` | 🟠 Alta |
| 04 | `04-load-testing.md` | `e2e-test-runner` | 🟡 Média |
| 05 | `05-imocv-integration-activate.md` | `celery-task-specialist`, `drf-viewset-builder` | 🟡 Média |

## Dependências

```
00 (bugfix) → PRIMEIRO — desbloqueia todo o resto
01 (CI/CD)  → depende de 00 (app tem de funcionar antes do deploy)
02 (seed)   → depende de 00 (dados carregados no staging)
03 (mobile) → independente — pode correr em paralelo com 01/02
04 (load)   → depende de 01 (precisa de ambiente staging)
05 (imo.cv) → depende de 00 + 02 (unidades reais para publicar)
```

## Definition of Done do Sprint 8

- [ ] Login funciona em Docker (Turbopack) e localmente
- [ ] `TENANT_DOMAIN` propagado correctamente em todos os environments
- [ ] GitHub Actions: lint + test + build + deploy em < 10 min
- [ ] Staging em DigitalOcean App Platform com dados de demo
- [ ] 2 promotoras piloto Cabo Verde registadas e activas
- [ ] App mobile testada em iOS (TestFlight) e Android (internal testing)
- [ ] Load test: 100 concurrent users, p95 < 500ms
- [ ] Unidades publicadas automaticamente no imo.cv após AVAILABLE
- [ ] `pytest tests/tenant_isolation/` — 100% passing
- [ ] SECURITY.md actualizado com bug bounty policy
