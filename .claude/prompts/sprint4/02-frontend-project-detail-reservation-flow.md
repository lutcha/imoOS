# Sprint 4 — Frontend: Project Detail + Fluxo de Reserva

## Pré-requisitos — Ler antes de começar

```
frontend/src/app/projects/page.tsx           → cards existentes, links para /projects/{id}
frontend/src/app/inventory/page.tsx          → tabela de unidades existente
frontend/src/components/crm/ReservationModal.tsx → modal existente (verificar estado)
frontend/src/hooks/useProjects.ts            → featureToProject(), useProject(id)
frontend/src/lib/api-client.ts              → apiClient configurado
```

Verificar rotas existentes:
```bash
ls frontend/src/app/projects/
ls frontend/src/app/inventory/
ls frontend/src/components/crm/
```

## Skills a carregar

```
@.claude/skills/04-frontend-nextjs/nextjs-tenant-routing/SKILL.md
@.claude/skills/04-frontend-nextjs/react-query-patterns/SKILL.md
@.claude/skills/05-module-tenants/tenant-branding/SKILL.md
@.claude/skills/06-module-projects/project-detail-view/SKILL.md
```

## Agents a activar (por esta ordem)

| Agent | Tarefa | Prompt |
|-------|--------|--------|
| `react-component-builder` | Project detail page | Ver Tarefa 1 abaixo |
| `react-component-builder` | Unidades por projecto (tab/section) | Ver Tarefa 2 abaixo |
| `react-component-builder` | Fluxo de reserva (modal→confirm) | Ver Tarefa 3 abaixo |
| `nextjs-tenant-routing` | Hooks: useProject, useProjectUnits | Ver Tarefa 4 abaixo |

---

## Tarefa 1 — `frontend/src/app/projects/[id]/page.tsx`

**Verificar** que `frontend/src/app/projects/[id]/` não existe antes de criar.

Prompt para `react-component-builder`:
> "Cria `frontend/src/app/projects/[id]/page.tsx` para ImoOS. Usa `useProject(id)` (já existe em `hooks/useProjects.ts`). Layout: breadcrumb (Projetos → Nome), hero com nome + localidade + status pill + % vendido, grid de stats (total unidades / disponíveis / reservadas / em contrato), mapa PostGIS (placeholder div com coordenadas se não houver mapa), tabs: Unidades | Documentos | Histórico. Tab Unidades usa `useProjectUnits(projectId)` — criar este hook. Skeleton durante loading. Tailwind + design system existente."

**Dados necessários do projecto:**
```typescript
interface ProjectDetail {
  id: string;
  name: string;
  description: string;
  status: 'PLANNING' | 'CONSTRUCTION' | 'COMPLETED' | 'ON_HOLD';
  location_name: string;
  total_units: number;
  available_units: number;
  reserved_units: number;
  contracted_units: number;
  // GeoJSON geometry — apenas coordenadas para placeholder
  geometry?: { type: string; coordinates: number[][] };
}
```

---

## Tarefa 2 — Hook `useProjectUnits` + tabela de unidades por projecto

Prompt para `react-component-builder` (ou estender inventory page existente):
> "Cria `frontend/src/hooks/useProjectUnits.ts`. Chama `GET /api/v1/inventory/units/?project={projectId}`. Usa React Query com key `['units', schema, projectId]`. Cria componente `ProjectUnitsTable` (separado, reutilizável) com colunas: Código, Tipologia, Área, Piso, Preço CVE, Estado, Acções. Coluna Acções: botão 'Reservar' (só se status=AVAILABLE e user tem role ≥ vendedor). Ao clicar 'Reservar', abre `ReservationModal` passando o `unitId`. NÃO duplicar o código da tabela de inventory/page.tsx — extrair para componente partilhado se necessário."

---

## Tarefa 3 — Fluxo de Reserva completo

**Ler `ReservationModal.tsx` primeiro** — verificar o estado actual antes de qualquer edição.

Prompt para `react-component-builder`:
> "Completa o `ReservationModal.tsx` para ImoOS. Deve: (1) receber `unitId` e `leadId` (ou permitir seleccionar lead numa listagem), (2) chamar `POST /api/v1/crm/reservations/create-reservation/`, (3) mostrar spinner durante pending, (4) sucesso → invalidar queries `['units', schema]` e `['reservations', schema]` via `queryClient.invalidateQueries`, (5) erro 400 (unit já reservada) → mostrar mensagem clara. Usar `useMutation` do React Query. Internacionalização: pt-PT."

Hook a criar em `frontend/src/hooks/useReservations.ts`:
```typescript
export function useCreateReservation() {
  const queryClient = useQueryClient();
  const { claims } = useAuth();

  return useMutation({
    mutationFn: (data: { unit_id: string; lead_id: string; notes?: string }) =>
      apiClient.post('/crm/reservations/create-reservation/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['units', claims?.tenant_schema] });
      queryClient.invalidateQueries({ queryKey: ['reservations', claims?.tenant_schema] });
      queryClient.invalidateQueries({ queryKey: ['leads', claims?.tenant_schema] });
    },
  });
}
```

---

## Tarefa 4 — Contratos: página de listagem

**Verificar** que `frontend/src/app/contracts/` não existe.

Página simples de listagem para esta sprint:
- Tabela: Nº Contrato, Lead, Unidade, Valor CVE, Estado, Data Assinatura
- Status pill com cores (DRAFT=cinza, ACTIVE=verde, COMPLETED=azul, CANCELLED=vermelho)
- Link para futuro detalhe `/contracts/{id}`
- Hook `useContracts()` via `GET /api/v1/contracts/contracts/`

---

## Verificação final

- [ ] `/projects/{id}` carrega dados correctos via API
- [ ] Tab "Unidades" mostra unidades do projecto
- [ ] Botão "Reservar" em unidade AVAILABLE → abre modal
- [ ] Reserva bem-sucedida → unit muda de status na tabela sem reload
- [ ] Reserva falhada (unit já reservada) → erro visível ao utilizador
- [ ] `/contracts` lista contratos do tenant
- [ ] `npm run build` sem erros TypeScript
- [ ] Sem console errors no browser
