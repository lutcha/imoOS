# Sprint 5 — Índice de Prompts

**Período:** Semana 9–11 (pré-Release 1)
**Data de criação:** 13 Mar 2026
**Estado Sprint 4:** 100% COMPLETO

## Contexto — o que existe vs o que falta

### Apps Django criadas mas VAZIAS (oportunidade)
- `apps/construction/` — directório vazio → Sprint 5 Prompt 02
- `apps/payments/` — directório vazio → Sprint 5 Prompt 04
- `apps/marketplace/` — directório vazio → Sprint 6
- `apps/sales/` — directório vazio → Sprint 6
- `apps/units/` — **LEGACY** duplicado de `apps/inventory` → Prompt 01 (cleanup)

### Frontend — o que falta
- `/` (Dashboard) — página existe mas `useTenantStats` precisa de dados reais
- `/payments` — não existe
- `/construction` — não existe
- Mobile: auth + sync + ecrãs — só schema WatermelonDB

## Ordem de execução

| # | Ficheiro | Agente(s) | Prioridade |
|---|----------|-----------|------------|
| 00 | `00-dashboard-analytics.md` | `react-component-builder`, `drf-viewset-builder` | 🔴 Alta — Release 1 |
| 01 | `01-cleanup-units-legacy.md` | `django-tenants-specialist`, `migration-orchestrator` | 🔴 Alta — dívida técnica |
| 02 | `02-backend-construction-module.md` | `model-architect`, `drf-viewset-builder`, `celery-task-specialist`, `isolation-test-writer` | 🟠 Média |
| 03 | `03-mobile-auth-sync-screens.md` | `react-component-builder` (RN) | 🟠 Média |
| 04 | `04-backend-payments-plans.md` | `model-architect`, `drf-viewset-builder`, `celery-task-specialist` | 🟡 Média |
| 05 | `05-frontend-construction-payments.md` | `react-component-builder`, `nextjs-tenant-routing` | 🟡 Baixa |

## Dependências

```
01 (units cleanup) → pode correr em paralelo com 00
02 (construction backend) → 05 (construction frontend)
04 (payments backend) → 05 (payments frontend)
03 (mobile) → independente
```

## Definition of Done do Sprint 5

- [ ] Dashboard `/` com métricas reais: unidades vendidas/disponíveis, receita, leads por stage
- [ ] `apps/units/` legacy removido ou migrado correctamente
- [ ] `apps/construction/` com DailyReport + Photo + ProgressUpdate models + API
- [ ] `apps/payments/` com PaymentPlan + Installment models + API
- [ ] Mobile: login funcional + listagem de projectos offline-first em Expo Go
- [ ] `pytest tests/tenant_isolation/` — 100% passing (sem regressões)
- [ ] `npm run build` sem erros TypeScript

## O que NÃO está neste sprint

- Integração imo.cv marketplace (Sprint 6)
- Portal de investidores (Sprint 6)
- Billing / planos SaaS (Sprint 6)
- E-signature em contratos (Sprint 7)
