# Sprint 6 — Índice de Prompts

**Período:** Semana 12–15 (Release 2 prep)
**Data de criação:** 13 Mar 2026
**Estado Sprint 5:** 100% COMPLETO

## Contexto — o que existe vs o que falta

### Apps Django vazias (prontas para receber código)
- `apps/marketplace/` — vazio → Prompt 01
- `apps/sales/` — vazio → Prompt 02

### Frontend — rotas em falta
- `/marketplace` — não existe
- `/investors` — não existe
- `/billing` — não existe (admin de planos SaaS)

### Funcionalidades críticas para Release 2
- Integração imo.cv (publicar unidades, sync de status)
- Portal de investidores (relatórios, documentos)
- Billing / planos SaaS (Free/Pro/Enterprise)
- E-signature em contratos
- Mobile: push sync (relatórios de obra)

## Ordem de execução

| # | Ficheiro | Agente(s) | Prioridade |
|---|----------|-----------|------------|
| 00 | `00-marketplace-imocv-integration.md` | `celery-task-specialist`, `drf-viewset-builder`, `model-architect` | 🔴 Release 2 crítico |
| 01 | `01-investors-portal.md` | `model-architect`, `drf-viewset-builder`, `react-component-builder` | 🟠 Alta |
| 02 | `02-billing-saas-plans.md` | `model-architect`, `drf-viewset-builder`, `celery-task-specialist` | 🟠 Alta |
| 03 | `03-esignature-contracts.md` | `drf-viewset-builder`, `celery-task-specialist` | 🟡 Média |
| 04 | `04-mobile-push-sync-construction.md` | `react-component-builder` (RN), `celery-task-specialist` | 🟡 Média |
| 05 | `05-whatsapp-automation.md` | `celery-task-specialist`, `drf-viewset-builder` | 🟢 Baixa |

## Dependências

```
00 (marketplace) → independente
01 (investors) → independente
02 (billing) → 00 + 01 (limitar features por plano)
03 (e-signature) → depende de 02 para plano Pro+
04 (mobile push) → depende de Sprint 5 mobile (pull sync ✅)
05 (whatsapp) → independente
```

## Definition of Done do Sprint 6

- [ ] `apps/marketplace/` com sync imo.cv — publicar unidade, receber leads
- [ ] Task periódica de sync de disponibilidade para imo.cv
- [ ] Portal de investidores com relatórios de rendimento e documentos
- [ ] `apps/billing/` com planos e limites enforçados
- [ ] E-signature integrada no fluxo de activação de contrato
- [ ] Mobile: relatório de obra com fotos submetido offline → sync ao conectar
- [ ] WhatsApp templates por tenant (não hardcoded)
- [ ] `pytest tests/tenant_isolation/` — 100% passing
