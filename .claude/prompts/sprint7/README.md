# Sprint 7 — Índice de Prompts

**Período:** Semana 16–19 (Release 3 prep — Go-Live Cabo Verde)
**Data de criação:** 14 Mar 2026
**Estado Sprint 6:** 100% COMPLETO

## Contexto — Sprint 7 = Go-Live readiness

Os Sprints 1–6 completaram toda a funcionalidade de negócio core. O Sprint 7 foca-se
em **qualidade de produção** — o que falta para colocar em produção real em Cabo Verde:

- Performance e observabilidade (sem métricas, não sabemos o que está partido em prod)
- Qualidade do frontend (zero testes de UI actualmente)
- Admin backoffice funcional (django-admin ou UI dedicada)
- Onboarding de novos tenants (self-service ou assistido)
- Relatórios e exportações (PDF, Excel — necessidade real das promotoras)
- Segurança hardening (pentest básico + rate limiting completo)

## Ordem de execução

| # | Ficheiro | Agente(s) | Prioridade |
|---|----------|-----------|------------|
| 00 | `00-observability-monitoring.md` | `celery-task-specialist`, `drf-viewset-builder` | 🔴 Go-Live crítico |
| 01 | `01-frontend-tests-storybook.md` | `e2e-test-runner`, `react-component-builder` | 🟠 Alta |
| 02 | `02-admin-backoffice.md` | `drf-viewset-builder`, `react-component-builder` | 🟠 Alta |
| 03 | `03-tenant-onboarding-flow.md` | `model-architect`, `nextjs-tenant-routing` | 🟡 Média |
| 04 | `04-reports-exports.md` | `celery-task-specialist`, `drf-viewset-builder` | 🟡 Média |
| 05 | `05-security-hardening.md` | `schema-isolation-auditor`, `drf-viewset-builder` | 🟡 Média |

## Dependências

```
00 (observability) → independente — fazer primeiro
01 (frontend tests) → independente — pode correr em paralelo com 00
02 (admin) → depende de 00 (health endpoint)
03 (onboarding) → depende de 02 (admin UI para aprovar tenants)
04 (exports) → independente
05 (security) → deve ser o último (auditar o sistema completo)
```

## Definition of Done do Sprint 7

- [ ] Sentry configurado e a receber erros de produção
- [ ] Health check endpoint `/health/` com status de db/redis/celery
- [ ] Prometheus metrics exportados (django-prometheus)
- [ ] Testes de componentes React com Vitest (coverage ≥ 80% em componentes core)
- [ ] E2E Playwright a passar em CI (auth, CRM, contratos, investidor)
- [ ] Django Admin customizado para super-admin (ver todos os tenants)
- [ ] Self-service onboarding: promotora cria conta, escolhe plano, paga
- [ ] Relatório de vendas por projecto em PDF (exportável)
- [ ] `pytest tests/tenant_isolation/` — 100% passing
- [ ] Rate limiting auditado e documentado
