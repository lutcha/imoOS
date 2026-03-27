# Sprint 4 — Índice de Prompts

**Data:** 2026-03-12
**Objectivo:** Fechar dívida crítica de auth, módulo de contratos, E2E, staging e spike mobile.

## Ordem de execução

| # | Ficheiro | Agente(s) | Prioridade |
|---|----------|-----------|------------|
| 00 | `00-dia0-middleware-auth-gate.md` | `nextjs-tenant-routing` | 🔴 CRÍTICO — fazer primeiro |
| 01 | `01-backend-contracts-module.md` | `model-architect` → `drf-viewset-builder` → `celery-task-specialist` → `isolation-test-writer` | 🟠 Alta |
| 02 | `02-frontend-project-detail-reservation-flow.md` | `react-component-builder` (×3), `nextjs-tenant-routing` | 🟠 Alta (depende de 00) |
| 03 | `03-e2e-playwright-tests.md` | `e2e-test-runner` | 🟡 Média (depende de 00 + 02) |
| 04 | `04-staging-digitalocean-cd.md` | `general-purpose` | 🟡 Média (paralelo com 01) |
| 05 | `05-mobile-spike-react-native.md` | `general-purpose` | 🟢 Spike / paralelo |

## Dependências

```
00 (middleware) ──► 02 (frontend pode verificar auth)
                └──► 03 (E2E auth tests)
01 (contracts backend) ──► 02 (botão reserva → activa contrato)
04 (staging) ──► 03 (E2E em staging URL real)
```

## O que está confirmado como feito (Sprint 3)

### Backend
- `apps/crm/models.py` — Lead (7 stages), UnitReservation + UniqueConstraint + HistoricalRecords ✅
- `apps/crm/services.py` — create_reservation (SELECT FOR UPDATE), cancel, convert, advance_lead_stage ✅
- `apps/crm/views.py` — pipeline, move_stage, schedule_visit, send_proposal, ReservationViewSet ✅
- `apps/crm/tasks.py` — notify_whatsapp, expire_reservations, send_visit_reminders, generate_proposal_pdf ✅

### Frontend
- `frontend/src/app/crm/page.tsx` — KanbanBoard + List toggle ✅
- `frontend/src/components/crm/` — KanbanBoard, KanbanColumn, LeadCard, ReservationModal ✅
- `frontend/src/app/settings/page.tsx` — tabs Branding, CRM, Reservas, Integrações ✅

### Testes
- `tests/tenant_isolation/test_jwt_isolation.py` — 10 testes, 3 classes ✅
- `tests/tenant_isolation/test_reservation_isolation.py` — 4 classes (threading) ✅

## Definition of Done do Sprint 4

- [ ] `frontend/src/middleware.ts` existe e protege todas as rotas
- [ ] `apps/contracts/` completo: modelos, views, serializers, URLs, migrations, PDF task
- [ ] `/projects/{id}` com listagem de unidades e botão "Reservar"
- [ ] Fluxo de reserva end-to-end: UI → API → SELECT FOR UPDATE → unit.status=RESERVED
- [ ] `tests/e2e/auth.spec.ts` + `crm-kanban.spec.ts` passando em CI
- [ ] Deploy automático para staging no push para `develop`
- [ ] Mobile spike: auth + listagem offline funcionais em Expo Go
- [ ] `pytest tests/tenant_isolation/ -v` — todos passing (sem regressões)
- [ ] `npm run build` sem erros TypeScript

## O que NÃO está neste sprint

- Push sync bidirecional mobile (Sprint 5)
- Dashboard de analytics / métricas (Sprint 5)
- Módulo de Obra / Construction (Sprint 5)
- Integração imo.cv marketplace (Sprint 6)
- Investidores portal (Sprint 6)
