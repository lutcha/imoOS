# Sprint 5 — Frontend: Obra + Pagamentos

## Pré-requisitos — Ler antes de começar

```
frontend/src/app/contracts/page.tsx   → padrão de listagem existente
frontend/src/hooks/useContracts.ts    → padrão de hook existente
frontend/src/components/ui/           → Skeleton, StatusBadge existentes
frontend/src/lib/format.ts            → formatCve, formatDate existentes
```

**Dependência:** Prompts 02 e 04 (backends) devem estar completos antes deste.

## Skills a carregar

```
@.claude/skills/04-frontend-nextjs/react-query-patterns/SKILL.md
@.claude/skills/11-module-construction/daily-report/SKILL.md
@.claude/skills/12-module-payments/payment-plan-generator/SKILL.md
@.claude/skills/05-module-tenants/tenant-branding/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `react-component-builder` | Página de Obra + formulário de relatório diário |
| `react-component-builder` | Plano de pagamentos por contrato |
| `nextjs-tenant-routing` | Adicionar rotas ao Sidebar |

---

## Tarefa 1 — Hook `useConstruction`

Criar `frontend/src/hooks/useConstruction.ts`:

```typescript
export interface DailyReport { /* mapear campos do serializer */ }
export interface ConstructionPhoto { /* s3_key, thumbnail_s3_key, caption, lat, lng */ }

export function useDailyReports(filters?: { project?: string; status?: string }) { ... }
export function useCreateDailyReport() { /* useMutation */ }
export function useSubmitReport() { /* POST /construction/daily-reports/{id}/submit/ */ }
```

---

## Tarefa 2 — Página `/construction`

Prompt para `react-component-builder`:
> "Cria `frontend/src/app/construction/page.tsx` para ImoOS. Listagem de relatórios diários com filtros: projecto, status (DRAFT/SUBMITTED/APPROVED), intervalo de datas. Tabela: Data | Projecto | Edifício | Progresso % | Autor | Estado | Nº Fotos. Skeleton durante loading. Botão 'Novo Relatório' abre drawer/modal. Seletor de projecto usa `useProjects()` existente. Design consistente com `/contracts/page.tsx`."

### Componente `DailyReportForm`

```typescript
// Campos: project (select), building (select dependente), date, summary, progress_pct (slider 0-100), weather, workers_count
// Upload de fotos: aceita múltiplos ficheiros, mostra preview, envia via S3 presigned URL existente
// Submit → onSuccess: invalidate useQuery(['construction'])
```

---

## Tarefa 3 — Plano de Pagamentos no detalhe do contrato

O `/contracts` é uma listagem — para o plano de pagamentos, adicionar uma **vista de detalhe** ou um **drawer**.

Prompt para `react-component-builder`:
> "Cria `frontend/src/app/contracts/[id]/page.tsx`. Mostra detalhes do contrato. Secção 'Plano de Pagamentos': tabela com prestações (tipo, valor CVE, data prevista, referência MBE, estado). Botão 'Gerar Plano' (se não existe) chama `POST /payments/plans/{id}/generate/`. Cada prestação tem badge PENDING/PAID/OVERDUE. Botão 'Marcar como Pago' chama o `mark-paid` existente."

Hook a criar `frontend/src/hooks/usePaymentPlans.ts`:
```typescript
export function usePaymentPlan(contractId: string) { ... }
export function useGeneratePaymentPlan() { /* useMutation: POST /payments/plans/ + /generate/ */ }
```

---

## Tarefa 4 — Sidebar: adicionar Obra

**Ler `frontend/src/components/layout/Sidebar.tsx` antes de editar.**

Adicionar entre CRM e Contratos:
```typescript
{ icon: HardHat, label: "Obra", href: "/construction" },
```
```typescript
import { HardHat } from "lucide-react";
```

---

## Verificação final

- [ ] `/construction` — listagem de relatórios com filtros
- [ ] Formulário de novo relatório — submissão cria `DailyReport` via API
- [ ] `/contracts/{id}` — plano de pagamentos com referências MBE
- [ ] Botão "Gerar Plano" → tabela de prestações aparece
- [ ] Badge OVERDUE aparece em prestações com `due_date < hoje` e `status=PENDING`
- [ ] Sidebar tem link "Obra" com ícone HardHat
- [ ] `npm run build` sem erros TypeScript
