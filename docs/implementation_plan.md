# ImoOS — Plano de Implementação (Actualizado: 11 Mar 2026)

**Tech Lead:** Agente Claude
**Status:** Sprint 1 em curso — Backend APIs + Frontend Shell prontos
**Próximo Milestone:** Release 1 — Semana 12

---

## PROGRESSO GERAL

```
Sprint 0  [██████████] COMPLETA — estrutura, skills, 10 agents, CI/CD, modelos base
Sprint 1  [████░░░░░░] EM CURSO — APIs users/projects/inventory, frontend layout/dashboard
Sprint 2  [░░░░░░░░░░] CRM + imo.cv sync
...
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
- [x] `apps/crm/models.py` + serializers + views + urls — Lead, Interaction
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
- [x] **10 Agents** em `.claude/agents/` (ver secção Agents abaixo)

### Frontend — Iniciado
- [x] Next.js 14 + TypeScript + Tailwind — setup completo
- [x] `Sidebar.tsx` — navegação com active state, ícones Lucide
- [x] `Topbar.tsx` — pesquisa, notificações, user avatar
- [x] `app/layout.tsx` — RootLayout com sidebar + topbar
- [x] `app/page.tsx` — Dashboard com KPI cards (estático) + "Projetos Recentes"

### Testes
- [x] `tests/conftest.py` — fixtures tenant_a, tenant_b, api_client_a
- [x] `tests/tenant_isolation/test_core_isolation.py` — gate obrigatório

---

## 🔄 SPRINT 1 — EM CURSO (Semanas 2-3)

### Como usar Skills e Agents nesta Sprint

| Tarefa | Skill a usar | Agent a activar |
|--------|-------------|-----------------|
| Novo ViewSet ou Serializer | `/drf-viewset-template` `/serializer-patterns` | `drf-viewset-builder` |
| Modelo novo com audit | `/model-audit-history` `/tenant-aware-queries` | `model-architect` |
| Verificar isolamento tenant | `/cross-tenant-prevention` | `tenant-expert` (auditoria) |
| Task Celery nova | `/celery-safe-pattern` `/tenant-task-wrapper` | `celery-task-specialist` |
| Componente React | `/tailwind-design-tokens` `/react-query-tenant` | `react-component-builder` |
| Testes de isolamento | `/isolation-test-template` `/pytest-tenant-fixtures` | `isolation-test-writer` |

---

### 🟠 Backend — Completar APIs (Semana 2, Dias 1-3)

**Assignado a:** Backend Dev 2

Os modelos e ViewSets básicos existem. O que falta:

1. **`apps/inventory/filters.py`** — UnitFilter avançado
   - Filtros: status, unit_type, floor, price_cve__range, area_bruta__range
   - Usar skill: `/django-filters-setup`

2. **`apps/crm/` — verificar completude**
   - Lead (source, status, assigned_to), Interaction model
   - LeadViewSet com pipeline action
   - Usar skill: `/lead-qualification-flow`

3. **`apps/users/views.py` — endpoint /me/ com IsTenantMember**
   - O ViewSet existe mas falta a permission `IsTenantMember`
   - Usar agent: `tenant-expert` para auditar o ViewSet

4. **Tenant isolation tests — expandir**
   - Testar: JWT de tenant_a rejeitado em tenant_b
   - Testar: Unit de tenant_a não visível para tenant_b
   - Usar skill: `/isolation-test-template`
   - Usar agent: `isolation-test-writer`

5. **Management command `create_tenant`**
   - Criar Client + Domain + TenantSettings + superuser inicial
   - Usar skill: `/management-commands` + `/tenant-onboarding-flow`

---

### 🟡 Frontend — Auth + API Integration (Semana 2, Dias 2-5)

**Assignado a:** Frontend Dev

O layout e dashboard estático existem. O que falta:

1. **Auth flow** — login page com JWT, httpOnly cookies, refresh automático
   - Usar skill: `/auth-jwt-handling`
   - Usar agent: `nextjs-tenant-routing`

2. **API client** — axios com `Authorization` header automático
   - Usar skill: `/api-client-tenant-header`

3. **TanStack Query setup** — QueryClient com tenant-scoped keys
   - Usar skill: `/react-query-tenant`

4. **Tenant detection** — subdomain → tenant slug → header
   - Usar skill: `/nextjs-tenant-routing`
   - Usar agent: `nextjs-tenant-routing`

5. **`useProjects()` hook** — primeiro hook real com React Query
   - Usar skill: `/react-query-tenant`

6. **Dashboard dinâmico** — substituir dados estáticos por API real
   - Usar agent: `react-component-builder`

---

### 🟢 DevOps (Semana 2)

1. Push para GitHub — main + develop branches
2. Branch protection — CI obrigatório + 1 review
3. Staging DigitalOcean — App Platform ou Droplet
4. Sentry configurado em staging

---

## 📋 SPRINT 2 — SEMANAS 4-6

### Como usar Skills e Agents nesta Sprint

| Tarefa | Skill a usar | Agent a activar |
|--------|-------------|-----------------|
| Tenant onboarding wizard | `/tenant-onboarding-flow` `/tenant-branding-config` | `react-component-builder` |
| Tabela de unidades com filtros | `/unit-status-workflow` `/unit-pricing-currency` | `react-component-builder` |
| Upload de plantas (S3) | `/unit-media-s3-upload` | `drf-viewset-builder` |
| Pipeline CRM Kanban | `/sales-pipeline-kanban` `/lead-source-tracking` | `react-component-builder` |
| Notificações Celery + WhatsApp | `/async-email-whatsapp` `/celery-beat-scheduling` | `celery-task-specialist` |
| Auditoria multi-tenant | `/cross-tenant-prevention` | `tenant-expert` + `schema-isolation-auditor` |

### Backend

1. **`apps/tenants/views.py`** — TenantOnboardingView, TenantSettingsView
   - Usar skill: `/tenant-onboarding-flow`
   - Usar agent: `django-tenants-specialist`

2. **Upload media** — S3 presigned URLs para plantas/renders de unidades
   - Usar skill: `/unit-media-s3-upload`
   - Usar agent: `drf-viewset-builder`

3. **Celery: bulk import CSV de unidades**
   - Usar skill: `/unit-bulk-import-csv` + `/celery-safe-pattern`
   - Usar agent: `celery-task-specialist`

4. **Celery: notificação WhatsApp na reserva**
   - Usar skill: `/async-email-whatsapp` + `/tenant-task-wrapper`
   - Usar agent: `celery-task-specialist`

### Frontend

1. **Página Inventário** — tabela com filtros, paginação, status badge colorido
   - Usar agent: `react-component-builder` + `tailwind-design-system`

2. **Formulário criar Projecto** — mapa interactivo + PostGIS
   - Usar skill: `/project-model-geojson`
   - Usar agent: `react-component-builder`

3. **Tenant onboarding wizard** — setup inicial da promotora
   - Usar skill: `/tenant-branding-config`
   - Usar agent: `react-component-builder`

---

## 📋 SPRINT 3 — SEMANAS 7-9 (Release 1 prep)

### Como usar Skills e Agents nesta Sprint

| Tarefa | Skill a usar | Agent a activar |
|--------|-------------|-----------------|
| CRM Pipeline Kanban | `/sales-pipeline-kanban` `/reservation-lock-mechanism` | `react-component-builder` |
| Reserva anti-double-booking | `/reservation-lock-mechanism` | `drf-viewset-builder` + `tenant-expert` |
| Relatório PDF | `/proposal-generation-pdf` | `drf-viewset-builder` |
| E2E tests | — | `isolation-test-writer` |

### Backend

1. **Reservas** — `UnitReservation` model com SELECT FOR UPDATE anti-double-booking
   - Usar skill: `/reservation-lock-mechanism`
   - Usar agent: `model-architect` + `tenant-expert` (validação)

2. **Relatório/proposta PDF** — geração com WeasyPrint
   - Usar skill: `/proposal-generation-pdf`

3. **CRM: pipeline actions** — qualifyLead, scheduledVisit, makeProposal
   - Usar skill: `/lead-qualification-flow` + `/visit-scheduling-calendar`
   - Usar agent: `drf-viewset-builder`

### Frontend

1. **CRM — Pipeline Kanban** — drag & drop, filtros por vendedor
   - Usar skill: `/sales-pipeline-kanban`
   - Usar agent: `react-component-builder`

2. **Offline indicator** — componente para utilizadores em obra
   - Usar skill: `/offline-first-pattern`

3. **i18n** — pt-PT base + preparação para pt-AO
   - Usar skill: `/i18n-l10n`

---

## 📋 RELEASE 2 — SEMANAS 13-22

### Como usar Skills e Agents

| Tarefa | Skill a usar | Agent a activar |
|--------|-------------|-----------------|
| Sync com imo.cv API | `/unit-availability-sync` | `celery-task-specialist` |
| Captura de leads imo.cv | `/lead-source-tracking` | `drf-viewset-builder` |
| Billing / planos SaaS | `/tenant-plan-limits` `/tenant-billing-webhook` | `model-architect` |
| Investor portal | — | `react-component-builder` + `nextjs-tenant-routing` |

### Épicos

- **INT-01: Integração imo.cv** — publicação de unidade, sync automático de status
- **CRM-02: WhatsApp automation** — notificações vendedor, templates por tenant
- **BIL-01: Billing** — planos Free/Pro/Enterprise, Stripe webhook

---

## 📋 RELEASE 3 — SEMANAS 23-36

### Como usar Skills e Agents

| Tarefa | Skill a usar | Agent a activar |
|--------|-------------|-----------------|
| Contratos PDF | `/contract-template-engine` `/e-signature-integration` | `drf-viewset-builder` |
| Planos de pagamento | `/payment-plan-generator` `/installment-scheduler` | `model-architect` |
| App de obra offline | `/offline-first-pattern` (mobile WatermelonDB) | `celery-task-specialist` |
| Auditoria LGPD | `/security-compliance` | `schema-isolation-auditor` |

### Épicos

- **FIN-01: Contratos** — template engine, e-signature, PDF gerado
- **FIN-02: Pagamentos** — planos parcelados, reconciliação MBE, dunning
- **OBRA-01: App Obra** — WatermelonDB offline-first, fotos com geotag, sync

---

## 🤖 AGENTS DISPONÍVEIS

Os agentes em `.claude/agents/` são subprocessos especializados. Invocar quando a tarefa for complexa e repetitiva.

### Arquitectura (`00-architecture/`)
| Agent | Quando usar |
|-------|------------|
| `tenant-expert` | Auditar qualquer PR/ViewSet para violações de isolamento — output ✅/⚠️/❌ |
| `django-tenants-specialist` | Decisões de arquitectura multi-tenant, migrations cross-tenant |
| `schema-isolation-auditor` | Auditoria periódica de toda a codebase |

### Backend (`01-backend/`)
| Agent | Quando usar |
|-------|------------|
| `model-architect` | Novo modelo de negócio — gera o modelo completo seguindo TenantAwareModel |
| `drf-viewset-builder` | Novo ViewSet — gera ViewSet + Serializer + URLs + filtros + testes |
| `celery-task-specialist` | Nova task assíncrona — garante tenant_context, idempotência, retry |

### Frontend (`02-frontend/`)
| Agent | Quando usar |
|-------|------------|
| `nextjs-tenant-routing` | Routing multi-tenant, middleware, subdomain detection |
| `react-component-builder` | Componente complexo (tabela, formulário, Kanban, modal) |
| `tailwind-design-system` | Design system tokens, variantes de componentes, tema por tenant |

### Testes (`03-testing/`)
| Agent | Quando usar |
|-------|------------|
| `isolation-test-writer` | Gerar suite completa de testes de isolamento para novo modelo/ViewSet |

---

## ⚠️ RISCOS ACTIVOS

| Risco | Status | Acção |
|-------|--------|-------|
| API imo.cv — sem documentação confirmada | 🔴 Bloqueante R2 | Reunião urgente com PO |
| WhatsApp Business API — aprovação pendente | 🟡 Monitorar | PO iniciar processo já |
| GDAL/PostGIS no CI runner | 🟡 Confirmar | Validar na primeira migration PostGIS |
| Frontend sem auth real | 🟡 Sprint 1 | Frontend Dev — auth flow esta semana |
| Mobile — zero progresso | 🟡 Sprint 2 | Spike WatermelonDB na Semana 4 |

---

## 📊 MÉTRICAS ALVO

| Métrica | Target | Actual |
|---------|--------|--------|
| Coverage apps core | ≥80% | — (a medir) |
| Isolation tests | 100% passing | — (a correr) |
| CI build time | <15 min | — |
| PR review time | <24h | — |
| Endpoints documentados (Swagger) | 100% | ~60% |

---

## 🛡️ REGRAS DEFENSIVAS (resumo)

1. Nunca escrever código sem ler o ficheiro existente primeiro
2. Isolation tests são gate de CI — nenhum merge sem eles a passar
3. Nenhuma query tenant sem `connection.schema_name` ou `tenant_context()`
4. Secrets apenas em env vars — nunca hardcoded
5. Toda a destruição (delete tenant) requer confirmação manual explícita
6. Correr `tenant-expert` agent em todo o PR que toque em models/views

Ver: [`DEFENSIVE.md`](DEFENSIVE.md)

---

## 📅 PRÓXIMAS ACÇÕES (Esta Semana)

### Tech Lead
- [ ] Push repositório para GitHub
- [ ] Configurar branch protection
- [ ] Distribuir tarefas Sprint 1

### Backend Dev 1
- [x] ~~`apps/users/models.py`~~ — feito pelo Antigravity agent
- [x] ~~JWT customizado com tenant_schema~~ — `TenantTokenObtainPairSerializer` existe
- [ ] Expandir testes de isolamento — User de tenant_a rejeitado em tenant_b
- [ ] `apps/inventory/filters.py` — UnitFilter com range de preços

### Backend Dev 2
- [x] ~~`apps/projects/` ViewSets~~ — feito
- [x] ~~`apps/inventory/` ViewSets~~ — feito agora
- [ ] Verificar `apps/crm/models.py` completude
- [ ] Management command `create_tenant`

### Frontend Dev
- [x] ~~Layout global (Sidebar + Topbar + Dashboard)~~ — feito
- [ ] Auth flow — login page + JWT
- [ ] API client axios com tenant header
- [ ] TanStack Query setup + `useProjects()` primeiro hook

### DevOps
- [ ] Staging DigitalOcean
- [ ] Sentry setup

---

*Actualizado por: Tech Lead Agent | 11 Mar 2026*
