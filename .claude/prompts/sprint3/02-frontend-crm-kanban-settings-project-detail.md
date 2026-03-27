# Sprint 3 — Frontend: CRM Kanban + Settings + Detalhe de Projecto

## Pré-requisitos

Ler antes de começar:
- `frontend/src/app/crm/page.tsx` — scaffold existente a substituir pelo Kanban
- `frontend/src/app/projects/[id]/page.tsx` — existe, verificar tabs implementadas
- `frontend/src/hooks/useLeads.ts` — hook existente a expandir
- `frontend/src/hooks/useProjects.ts` — hook existente com GeoJSON pattern

## Skills a carregar

```
@.claude/skills/08-module-crm/sales-pipeline-kanban/SKILL.md
@.claude/skills/08-module-crm/reservation-lock-mechanism/SKILL.md
@.claude/skills/08-module-crm/lead-qualification-flow/SKILL.md
@.claude/skills/04-frontend-nextjs/react-query-tenant/SKILL.md
@.claude/skills/05-module-tenants/tenant-branding-config/SKILL.md
@.claude/skills/04-frontend-nextjs/tailwind-design-tokens/SKILL.md
```

## Agents a activar

| Agent | Tarefa | Prompt sugerido |
|-------|--------|----------------|
| `react-component-builder` | Kanban board | "Cria componente `<KanbanBoard>` para ImoOS CRM. 7 colunas (new→contacted→visit_scheduled→proposal_sent→negotiation→won→lost). Drag entre colunas via @dnd-kit/core. Ao drop, chama `PATCH /api/v1/crm/leads/{id}/move-stage/`. Cards mostram nome, fonte, orçamento CVE, unidade de interesse. Coluna 'won' em verde, 'lost' em cinza." |
| `react-component-builder` | Modal de reserva | "Cria `<ReservationModal>` que abre ao clicar 'Reservar Unidade' num card de lead. Form: unit_id (dropdown das unidades AVAILABLE), deposit_amount_cve, expires_at (datepicker). Submit: `POST /api/v1/crm/reservations/create-reservation/`. Mostrar erro se unidade já reservada (409 do backend)." |
| `tailwind-design-system` | Consistência visual | "Verifica que o Kanban usa os mesmos design tokens que as páginas existentes (inventory, projects). Cores de stage: new=slate, contacted=blue, visit_scheduled=indigo, proposal_sent=amber, negotiation=orange, won=emerald, lost=slate/50." |
| `react-component-builder` | Settings page | "Cria página `/settings` para ImoOS. Tabs: Empresa (nome, timezone, moeda), Aparência (logo upload + preview, cor primária com colorpicker), Integrações (imo.cv API key, WhatsApp phone ID — campos write-only com reveal button). Usa `GET/PATCH /api/v1/tenant/settings/`." |

---

## Tarefa 1 — `/crm` — Substituir scaffold pelo Kanban

**Ficheiro:** `frontend/src/app/crm/page.tsx` — **ler antes de editar**.

### Estrutura do componente

```
CRMPage
├── Header: "CRM — Pipeline de Vendas" | btn "Novo Lead" | btn "Vista Lista" ↔ "Vista Kanban"
├── KanbanView (default)
│   └── KanbanBoard
│       ├── KanbanColumn × 7 (new, contacted, visit_scheduled, proposal_sent, negotiation, won, lost)
│       │   ├── ColHeader: label + count badge
│       │   └── LeadCard × N
│       │       ├── Nome + fonte badge
│       │       ├── Unidade de interesse (se definida)
│       │       ├── Orçamento em CVE
│       │       └── Acções: "Ver" | "Reservar" | "Mover"
└── ListView (fallback toggle)
    └── Tabela simples (reutilizar padrão do Inventário)
```

### Hook expandido: `useLeads.ts`

Ler o ficheiro existente. Adicionar:
```typescript
// Grouped by stage — útil para o Kanban
export function useLeadsByStage() {
  const { schema } = useTenant();
  return useQuery({
    queryKey: ['leads', schema, 'by-stage'],
    queryFn: () => apiClient.get('/crm/leads/?page_size=200').then(r => r.data),
    select: (data) => groupByStage(data.results),
    staleTime: 15_000,
  });
}

// Mutation: move stage
export function useMoveLeadStage() {
  const qc = useQueryClient();
  const { schema } = useTenant();
  return useMutation({
    mutationFn: ({ id, stage }: { id: string; stage: string }) =>
      apiClient.patch(`/crm/leads/${id}/move-stage/`, { stage }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads', schema] }),
  });
}
```

### Dependência: `@dnd-kit/core`

```bash
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

**Padrão de drag-and-drop:**
- `DndContext` envolve o `KanbanBoard`
- `onDragEnd`: extrair `active.id` (lead id) e `over.id` (stage de destino)
- Optimistic update: actualizar o estado local imediatamente, depois disparar a mutation
- Em caso de erro da mutation: reverter o estado local e mostrar toast de erro

---

## Tarefa 2 — `/projects/[id]` — Verificar e completar tabs

**Ficheiro:** `frontend/src/app/projects/[id]/page.tsx` — **ler antes de editar**.

Se as tabs "Edifícios" e "Unidades" existem mas estão vazias:

**Tab "Unidades":** reutilizar `InventoryPage` como componente com `projectId` prop (filtro por projecto).
```typescript
// Em useUnits.ts — já deve existir o suporte a filtro 'project'
const { data } = useUnits({ project: id });
```

**Tab "Edifícios":** `useBuildings(projectId)` → lista de edifícios com accordion de pisos.
```typescript
// Novo hook: useBuildings
export function useBuildings(projectId: string) {
  const { schema } = useTenant();
  return useQuery({
    queryKey: ['buildings', schema, projectId],
    queryFn: () => apiClient.get(`/projects/buildings/?project=${projectId}`).then(r => r.data),
  });
}
```

---

## Tarefa 3 — `/settings` — Página de configurações do tenant

**Ficheiro a criar:** `frontend/src/app/settings/page.tsx`

```
SettingsPage
├── Tabs: [Empresa] [Aparência] [Integrações] [Membros]
│
├── Tab "Empresa"
│   ├── nome da empresa (PATCH /tenant/settings/)
│   ├── timezone (select com timezones)
│   └── moeda principal (CVE / EUR)
│
├── Tab "Aparência"
│   ├── Logo: upload directo para S3 via POST /tenant/s3-upload/ (resource_type=branding)
│   │   └── Preview do logo após upload
│   └── Cor primária: colorpicker (input type=color + hex manual)
│       └── Preview live: botão de exemplo com a cor escolhida
│
├── Tab "Integrações"
│   ├── imo.cv API Key: input type=password + botão "Revelar/Ocultar" + "Testar ligação"
│   └── WhatsApp Phone ID: idem
│
└── Tab "Membros" (scaffold — full invite flow no Sprint 4)
    └── Lista dos membros actuais com roles
```

**Hook:** `useTenantSettings` (já deve existir em `useTenantStats.ts` ou criar novo)
```typescript
export function useTenantSettings() { ... }  // GET /api/v1/tenant/settings/
export function useUpdateTenantSettings() { ... }  // PATCH /api/v1/tenant/settings/
```

---

## Tarefa 4 — Topbar — Mostrar dados reais do tenant

**Ficheiro:** `frontend/src/components/layout/Topbar.tsx` — **ler antes de editar**.

A Topbar mostra "Gestor Senior" e "Promotora ABC" hardcoded.
Substituir pelos dados reais do `AuthContext`:
```typescript
import { useAuth } from "@/contexts/AuthContext";
const { user, tenant } = useAuth();
// Usar: user.fullName, user.initials, tenant.name, user.role
```

---

## Verificação final

- [ ] Kanban carrega leads agrupados por stage
- [ ] Drag de um card entre colunas → `PATCH move-stage` disparado, Kanban actualizado optimisticamente
- [ ] `<ReservationModal>` cria reserva e actualiza status da unidade na tabela de inventário
- [ ] `/settings` → PATCH branding actualiza `primary_color` (verificar se Tailwind CSS var muda)
- [ ] `/projects/{id}` Tab Unidades → mostra unidades filtradas por projecto
- [ ] Topbar mostra nome real do user e nome real do tenant
- [ ] `npm run build` sem erros TypeScript
- [ ] Não usar dados hardcoded em nenhum dos componentes modificados
