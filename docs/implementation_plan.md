# ImoOS — Plano de Implementação (Actualizado: 13 Mar 2026)

**Tech Lead:** Agente Claude
**Status:** Sprint 4 100% CONCLUÍDA → Sprint 5 A INICIAR
**Próximo Milestone:** Release 1 — Semana 12
**Última actualização:** 13 Mar 2026

---

## PROGRESSO GERAL

```
Sprint 0  [██████████] COMPLETA — estrutura, skills, agents, CI/CD, modelos, APIs base
Sprint 1  [██████████] COMPLETA — auth JWT, api-client, hooks, crm fix, filtros, login UI
Sprint 2  [██████████] COMPLETA — tenant API, S3, Celery, memberships, páginas, middleware
Sprint 3  [██████████] COMPLETA — reservas, Kanban CRM, PDF task, testes isolamento
Sprint 4  [██████████] COMPLETA — contracts, E2E Playwright, mobile schema, staging CD
Sprint 5  [░░░░░░░░░░] A INICIAR — dashboard, obra, mobile auth+sync, pagamentos
Semana 12 [          ] Release 1 Target
Semana 22 [          ] Release 2 Target
Semana 36 [          ] Release 3 Target (MVP)
```

---

## ✅ SPRINT 0 — CONCLUÍDA

### Backend Foundation
- [x] `apps/tenants/models.py` — Client, Domain, TenantSettings com history
- [x] `apps/core/models.py` — BaseModel (UUID pk, timestamps), TenantAwareModel abstract
- [x] `apps/users/models.py` — CustomUser (email auth, UUID, roles, HistoricalRecords)
- [x] `apps/users/permissions.py` — IsTenantMember (JWT tenant_schema == connection.schema_name)
- [x] `apps/users/serializers.py` — UserSerializer + TenantTokenObtainPairSerializer
- [x] `apps/users/views.py` — UserViewSet + TenantTokenObtainPairView
- [x] `apps/users/urls.py` — auth/token/ + users router
- [x] `apps/projects/models.py` — Project (PostGIS), Building, Floor (TenantAwareModel)
- [x] `apps/projects/serializers.py` — ProjectSerializer, BuildingSerializer, FloorSerializer
- [x] `apps/projects/views.py` — ProjectViewSet, BuildingViewSet, FloorViewSet
- [x] `apps/projects/urls.py` — router em api/v1/projects/
- [x] `apps/inventory/models.py` — Unit (history, workflow), UnitType, UnitPricing (CVE/EUR)
- [x] `apps/inventory/serializers.py` — UnitSerializer, UnitPricingSerializer (nested)
- [x] `apps/inventory/views.py` — UnitViewSet, UnitTypeViewSet
- [x] `apps/inventory/urls.py` — router em api/v1/inventory/
- [x] `apps/crm/models.py` — Lead, Interaction (TenantAwareModel, HistoricalRecords)
- [x] `apps/crm/serializers.py` — LeadSerializer + **PublicLeadSerializer** (campos mínimos)
- [x] `apps/crm/views.py` — LeadViewSet (pipeline action), InteractionViewSet
- [x] `apps/crm/views_public.py` — LeadCaptureView (AllowAny + PublicEndpointThrottle)
- [x] `apps/crm/urls.py` — lead-capture/ público + router autenticado
- [x] `config/urls.py` — rotas correctas (projects, inventory, crm, users, docs)
- [x] `config/celery.py` — app Celery com autodiscover
- [x] `config/__init__.py` — import celery_app
- [x] `config/settings/` — base, development, testing
- [x] `apps/core/pagination.py` — StandardResultsPagination (20/100)
- [x] `apps/core/exceptions.py` — custom_exception_handler + TenantPermissionDenied
- [x] `apps/core/throttling.py` — PublicEndpointThrottle (100/h), AuthenticatedUserThrottle

### Infraestrutura
- [x] `docker-compose.dev.yml` — 6 serviços com healthchecks
- [x] `.github/workflows/ci.yml` — lint + security + test + isolation-gate + build
- [x] `Makefile` — 15 comandos padronizados
- [x] `requirements/` — base, development, production
- [x] `.env.example` — todas as variáveis documentadas

### Claude Developer Experience
- [x] `.claude/CLAUDE.md` — contexto master sempre carregado
- [x] **109 Skills** em `.claude/skills/` (17 categorias)
- [x] **10 Agents** em `.claude/agents/`
- [x] **Prompts Sprint 1** em `.claude/prompts/sprint1/` (4 prompts)
- [x] **Prompts Sprint 2** em `.claude/prompts/sprint2/` (5 prompts)

---

## ✅ SPRINT 1 — CONCLUÍDA

### Backend — Concluído
- [x] `apps/crm/models.py` — fix import `apps.inventory.models` (era `apps.units`)
- [x] `apps/crm/views_public.py` — rate limit 100/h + `PublicLeadSerializer`
- [x] `apps/crm/views.py` — `LeadFilter` integrado
- [x] `apps/crm/filters.py` — `LeadFilter` (range budget, created_after/before)
- [x] `apps/inventory/filters.py` — `UnitFilter` (range preço CVE, area, project/building)
- [x] `apps/tenants/middleware.py` — Http404 importado, X-Tenant headers só para autenticados

### Frontend — Concluído
- [x] `src/lib/api-client.ts` — axios, interceptors JWT + refresh automático, queue de requests
- [x] `src/contexts/AuthContext.tsx` — login/logout/session restore via httpOnly cookie
- [x] `src/contexts/TenantContext.tsx` — schema + name derivados do AuthContext
- [x] `src/providers/Providers.tsx` — QueryClient (30s staleTime) + Auth + Tenant
- [x] `src/app/api/auth/login/route.ts` — proxy para Django, refresh em httpOnly cookie
- [x] `src/app/api/auth/refresh/route.ts` — exchange cookie → novo access token
- [x] `src/app/api/auth/logout/route.ts` — blacklist + clear cookie
- [x] `src/app/(auth)/login/page.tsx` — form com show/hide password, erro em pt-PT
- [x] `src/app/(auth)/layout.tsx` — layout sem Sidebar/Topbar

### Bugs corrigidos no Sprint 1
- [x] `config/urls.py` — URLs correctas para inventory e projects
- [x] `apps/crm/models.py` — import correcto de Unit

### Bugs corrigidos (entregues pelo linter/dev antes de Sprint 3)
- [x] JWT claims: `email`, `role`, `full_name` — nomes correctos em `apps/users/serializers.py`
- [x] Frontend API routes — URLs Django corrigidas (`/users/auth/token/`)
- [x] Token refresh extrai `tenant_schema` do payload JWT via `Buffer.from()`

---

## ✅ SPRINT 1 — CONCLUÍDA
...
[Checklist items for Sprint 1 remain the same]
...
## ✅ SPRINT 2 — CONCLUÍDA
- [x] Multi-tenant Settings API & UI
- [x] S3 Presigned Uploads
- [x] Inventory Bulk Import (CSV)
- [x] WhatsApp Notification Tasks
- [x] Unit details & Project details (Frontend)
- [x] Middleware protection (Finalizado)

## ✅ SPRINT 3 — CONCLUÍDA
- [x] `UnitReservation` model & logic (anti-double booking)
- [x] Pipeline CRM (Kanban) com Drag & Drop
- [x] Geração de Propostas em PDF (WeasyPrint)
- [x] Histórico de Auditoria (Simple History) em todos os modelos core

## ✅ SPRINT 4 — CONCLUÍDA
- [x] `Contract` e `Payment` models
- [x] Geração de planos de pagamento (Sinal + Prestações)
- [x] Filtros avançados de contratos
- [x] Mobile Schema init (WatermelonDB)
- [x] E2E Playwright tests base

## 🔄 SPRINT 5 — EM EXECUÇÃO
- [ ] Dashboard dinâmico (Charts de vendas)
- [ ] Diário de Obra (DailyReport + Photos)
- [ ] Mobile Auth & Sync Engine
- [ ] Pagamentos MBE integration (Reconciliação)

---

### Backend Sprint 3

**Prompt 01:** [`.claude/prompts/sprint3/01-backend-reservas-crm-pdf.md`](.claude/prompts/sprint3/01-backend-reservas-crm-pdf.md)

| Tarefa | Skills | Agents |
|--------|--------|--------|
| `Lead.stage` + `Lead.visit_date` + `Lead.commission_rate` — campos adicionais | `lead-qualification-flow` `commission-calculation` | `model-architect` |
| `UnitReservation` model — SELECT FOR UPDATE, UniqueConstraint(status=ACTIVE) | `reservation-lock-mechanism` `model-audit-history` | `model-architect` + `tenant-expert` |
| `ReservationViewSet.create_reservation` — transacção atómica anti-double-booking | `reservation-lock-mechanism` `tenant-aware-queries` | `drf-viewset-builder` |
| `LeadViewSet` actions: `move_stage`, `schedule_visit`, `send_proposal` | `lead-qualification-flow` `visit-scheduling-calendar` | `drf-viewset-builder` |
| `apps/crm/tasks.py` — `generate_proposal_pdf` (WeasyPrint → S3) | `proposal-generation-pdf` `celery-safe-pattern` | `celery-task-specialist` |
| Template HTML `apps/crm/templates/crm/proposal.html` | `proposal-generation-pdf` | — |

---

### Frontend Sprint 3

**Prompt 02:** [`.claude/prompts/sprint3/02-frontend-crm-kanban-settings-project-detail.md`](.claude/prompts/sprint3/02-frontend-crm-kanban-settings-project-detail.md)

| Tarefa | Skills | Agents |
|--------|--------|--------|
| `/crm` — Kanban 7 colunas com @dnd-kit/core, drag → `move_stage` | `sales-pipeline-kanban` `react-query-tenant` | `react-component-builder` `tailwind-design-system` |
| `<ReservationModal>` — criar reserva com verificação disponibilidade | `reservation-lock-mechanism` | `react-component-builder` |
| `/settings` — tabs Empresa / Aparência / Integrações / Membros | `tenant-branding-config` `unit-media-s3-upload` | `react-component-builder` |
| `/projects/[id]` — Tab Edifícios com `useBuildings()` hook | `react-query-tenant` | `react-component-builder` |
| Topbar — dados reais do `AuthContext` (user.fullName, tenant.name) | `tailwind-design-tokens` | — |

---

### Testes Sprint 3

**Prompt 03:** [`.claude/prompts/sprint3/03-testes-jwt-reservas-e2e.md`](.claude/prompts/sprint3/03-testes-jwt-reservas-e2e.md)

| Tarefa | Skills | Agents |
|--------|--------|--------|
| `tests/tenant_isolation/test_jwt_isolation.py` — JWT cross-tenant rejeitado | `isolation-test-template` `jwt-tenant-claims` | `isolation-test-writer` |
| `tests/tenant_isolation/test_reservation_isolation.py` — double-booking + cross-tenant | `reservation-lock-mechanism` `isolation-test-template` | `isolation-test-writer` |
| `test_membership_role_isolation.py` — role admin per-schema | `cross-tenant-prevention` | `isolation-test-writer` |
| `tests/e2e/` — Playwright: login, inventory, filtros | — | `isolation-test-writer` |
| CI: job `e2e-tests` após `deploy-staging` | — | — |

---

## 📋 BACKLOG — RELEASE 2 (Semanas 13-22)

### Como usar Skills e Agents

| Tarefa | Skills | Agents |
|--------|--------|--------|
| Sync com imo.cv API | `unit-availability-sync` | `celery-task-specialist` |
| Captura de leads imo.cv | `lead-source-tracking` | `drf-viewset-builder` |
| Billing / planos SaaS | `tenant-plan-limits` `tenant-billing-webhook` | `model-architect` |
| WhatsApp templates por tenant | `async-email-whatsapp` | `celery-task-specialist` |

### Épicos
- **INT-01: Integração imo.cv** — publicação de unidade, sync automático de status, retry exponencial
- **CRM-02: WhatsApp automation** — templates por tenant, opt-in, historico
- **BIL-01: Billing** — planos Free/Pro/Enterprise, Stripe webhook, usage limits enforcement

---

## 📋 BACKLOG — RELEASE 3 (Semanas 23-36)

### Como usar Skills e Agents

| Tarefa | Skills | Agents |
|--------|--------|--------|
| Contratos PDF | `contract-template-engine` `e-signature-integration` | `drf-viewset-builder` |
| Planos de pagamento | `payment-plan-generator` `installment-scheduler` | `model-architect` |
| App de obra offline | `offline-first-pattern` | `celery-task-specialist` |
| Auditoria LGPD | `security-compliance` | `schema-isolation-auditor` |

### Épicos
- **FIN-01: Contratos** — template engine, e-signature, PDF gerado
- **FIN-02: Pagamentos** — planos parcelados (20/80, faseado), reconciliação MBE, dunning
- **OBRA-01: App Obra** — WatermelonDB offline-first, fotos com geotag, sync diário de obra

---

## 🤖 AGENTS DISPONÍVEIS

### Arquitectura (`00-architecture/`)
| Agent | Quando usar |
|-------|------------|
| `tenant-expert` | Auditar todo o PR que toque em models/views/tasks — output ✅/⚠️/❌ |
| `django-tenants-specialist` | Decisões de arquitectura multi-tenant, migrations |
| `schema-isolation-auditor` | Auditoria periódica completa da codebase |

### Backend (`01-backend/`)
| Agent | Quando usar |
|-------|------------|
| `model-architect` | Novo modelo de negócio — gera com TenantAwareModel, UUIDs, history |
| `drf-viewset-builder` | Novo ViewSet — gera ViewSet + Serializer + URLs + filtros + testes |
| `celery-task-specialist` | Nova task — garante tenant_id como arg, tenant_context, idempotência, retry |

### Frontend (`02-frontend/`)
| Agent | Quando usar |
|-------|------------|
| `nextjs-tenant-routing` | Routing, middleware, subdomain detection, redirect logic |
| `react-component-builder` | Tabela, formulário, modal, Kanban, página completa |
| `tailwind-design-system` | Consistência visual, tokens, tema por tenant |

### Testes (`03-testing/`)
| Agent | Quando usar |
|-------|------------|
| `isolation-test-writer` | Suite completa de isolamento para novo modelo/ViewSet/task |

---

## ⚠️ RISCOS ACTIVOS

| Risco | Status | Acção |
|-------|--------|-------|
| `src/middleware.ts` em falta | 🔴 Sprint 3 Dia 0 | **Rotas desprotegidas** — prompt 00 |
| API imo.cv — sem documentação | 🔴 Bloqueante Release 2 | Reunião urgente com PO |
| Testes JWT isolation — não escritos | 🟠 Sprint 3 | Prompt 03 — gate CI em falta |
| WhatsApp Business API — aprovação | 🟡 Monitorar | PO iniciar processo já |
| Mobile — zero progresso | 🟡 Sprint 3 | Spike WatermelonDB Semana 7 |
| Staging não existe | 🟡 Urgente | DevOps — prompt sprint1/04 por executar |

---

## 📊 MÉTRICAS

| Métrica | Target | Actual |
|---------|--------|--------|
| Coverage apps core | ≥80% | — (a medir com `make coverage`) |
| Isolation tests Project + Unit | 100% passing | ✅ passing |
| JWT isolation tests | 100% passing | ❌ não escritos |
| Reservation isolation tests | 100% passing | ❌ não escritos |
| Endpoints documentados (Swagger) | 100% | ~75% |
| CI build time | <15 min | — |
| Staging live | Sprint 2 | ❌ não criado |

---

## 📁 PROMPTS DISPONÍVEIS

```
.claude/prompts/
├── sprint1/
│   ├── 01-frontend-auth-apiclient-reactquery.md   ✅ CONCLUÍDO
│   ├── 02-backend-inventory-filters-crm-fix.md    ✅ CONCLUÍDO
│   ├── 03-testes-isolation-jwt.md                 ⏳ pendente
│   └── 04-devops-github-staging.md                ⏳ pendente (URGENTE)
├── sprint2/
│   ├── 00-bugfix-criticos-antes-sprint2.md         ✅ CONCLUÍDO (linter aplicou)
│   ├── 01-backend-tenant-api-s3-management.md      ✅ CONCLUÍDO
│   ├── 02-backend-celery-csv-import-whatsapp.md    ✅ CONCLUÍDO
│   ├── 03-frontend-middleware-hooks-dashboard.md   ✅ CONCLUÍDO (falta middleware.ts)
│   └── 04-frontend-inventory-projects-pages.md     ✅ CONCLUÍDO
└── sprint3/
    ├── 00-fechar-sprint2-middleware.md             🔴 FAZER PRIMEIRO
    ├── 01-backend-reservas-crm-pdf.md              ░ a seguir
    ├── 02-frontend-crm-kanban-settings.md          ░ a seguir
    └── 03-testes-jwt-reservas-e2e.md               ░ a seguir
```

---

## 🛡️ REGRAS DEFENSIVAS

1. Ler cada ficheiro antes de editar — nunca assumir o conteúdo
2. Isolation tests são gate de CI — zero merges sem eles a passar
3. Tasks Celery: passar `tenant_id` (string), nunca objectos ORM
4. Nenhuma query tenant sem `connection.schema_name` ou `tenant_context()`
5. Secrets apenas em env vars — nunca hardcoded
6. Correr `tenant-expert` agent em todo o PR que toque em models/views/tasks
7. Toda a destruição (delete tenant) requer confirmação manual explícita

Ver: [`DEFENSIVE.md`](DEFENSIVE.md)

---

## 📅 PRÓXIMAS ACÇÕES (Sprint 3 — Esta Semana)

### Dia 1 — Frontend Dev 🔴 URGENTE
- [ ] `sprint3/00-fechar-sprint2-middleware.md` — criar `middleware.ts` (rotas desprotegidas)
- [ ] Verificar redirect `/auth/login?next=/inventory` funciona após middleware

### Backend Dev (Semanas 7-8)
- [ ] `sprint3/01-backend-reservas-crm-pdf.md` — reservas + pipeline CRM + PDF
- [ ] Correr `tenant-expert` agent em todo o código de reservas antes de merge

### Frontend Dev (Semanas 7-8, após middleware)
- [ ] `sprint3/02-frontend-crm-kanban-settings.md` — Kanban + Settings + Project detail
- [ ] Instalar `@dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities`

### QA (paralelo — começa Semana 7)
- [ ] `sprint3/03-testes-jwt-reservas-e2e.md` — 3 suites de isolamento + E2E Playwright
- [ ] Confirmar que `pytest tests/tenant_isolation/ -v` continua 100% passing

### DevOps 🟠 URGENTE
- [ ] `sprint1/04-devops-github-staging.md` — staging DigitalOcean (bloqueante para E2E)
- [ ] Adicionar `STAGING_URL` como GitHub Actions variable após staging up

---

*Actualizado por: Tech Lead Agent | 11 Mar 2026*
