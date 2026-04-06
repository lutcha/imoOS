# Dashboard Desktop para Gestores - ImoOS

## Visão Geral

Dashboard completo para gestores acompanharem obras, estatísticas de construção e orçamentos.

## Estrutura

```
frontend/src/
├── app/dashboard/
│   ├── page.tsx              # Dashboard principal (/) - Visão geral
│   └── layout.tsx            # Layout do dashboard
│
├── app/construction/
│   ├── page.tsx              # Lista de obras (/construction)
│   ├── layout.tsx            # Layout de obras
│   └── [projectId]/
│       ├── page.tsx          # Detalhe da obra (/construction/[id])
│       ├── gantt/page.tsx    # Cronograma Gantt
│       ├── budget/page.tsx   # Orçamento da obra
│       └── progress/page.tsx # Progresso físico
│
├── components/dashboard/
│   ├── StatsCards.tsx        # Cards de estatísticas
│   ├── ObrasTable.tsx        # Tabela de obras com filtros
│   ├── ProgressChart.tsx     # Gráfico de progresso (Recharts)
│   ├── BudgetChart.tsx       # Gráfico orçamento vs real
│   ├── GanttChart.tsx        # Cronograma Gantt simplificado
│   ├── RecentActivity.tsx    # Atividade recente
│   └── index.ts              # Exportações
│
└── hooks/
    ├── useConstructionStats.ts  # Hooks de obras, fases, tarefas, gantt
    └── useBudgetStats.ts        # Hooks de orçamentos
```

## Hooks

### useConstructionStats

```typescript
// Lista de projetos de construção
const { data: projects } = useConstructionProjects({ page_size: 10 });

// Detalhe de um projeto
const { data: project } = useConstructionProject(projectId);

// Fases de uma obra
const { data: phases } = useConstructionPhases(projectId);

// Tarefas de uma obra
const { data: tasks } = useConstructionTasks(projectId);

// Dados para Gantt
const { data: ganttItems } = useGanttData(projectId);

// Estatísticas agregadas
const { data: stats } = useConstructionAggregatedStats();
```

### useBudgetStats

```typescript
// Lista de orçamentos
const { data: budgets } = useBudgets({ project: projectId });

// Detalhe de um orçamento
const { data: budget } = useBudget(budgetId);

// Estatísticas de orçamento
const { data: stats } = useBudgetStats(projectId);
```

## Componentes

### StatsCards

```typescript
import { ConstructionStatsCards, DashboardStatsCards } from "@/components/dashboard";

// Cards específicos de construção
<ConstructionStatsCards stats={stats} isLoading={isLoading} />

// Cards do dashboard geral
<DashboardStatsCards 
  period="30d" 
  stats={dashboardStats} 
  constructionStats={constructionStats}
  isLoading={isLoading} 
/>
```

### ObrasTable

```typescript
import { ObrasTable } from "@/components/dashboard";

<ObrasTable 
  projects={projects} 
  isLoading={isLoading}
  error={error}
/>
```

Funcionalidades:
- Pesquisa por nome/descrição
- Filtro por status
- Ordenação por colunas
- Indicadores de orçamento excedido (>10%)

### ProgressChart

```typescript
import { ProgressChart } from "@/components/dashboard";

<ProgressChart 
  projects={projects} 
  isLoading={isLoading}
  maxItems={8}
/>
```

### BudgetChart

```typescript
import { BudgetChart } from "@/components/dashboard";

<BudgetChart stats={budgetStats} isLoading={isLoading} />
```

### GanttChart

```typescript
import { GanttChart } from "@/components/dashboard";

<GanttChart 
  items={ganttItems} 
  isLoading={isLoading}
  startDate={project.start_date}
  endDate={project.expected_end_date}
/>
```

## Rotas

| Rota | Descrição |
|------|-----------|
| `/` | Dashboard Geral (já existente) |
| `/dashboard` | Dashboard de Gestão (obras) |
| `/construction` | Lista de Obras |
| `/construction/[id]` | Detalhe da Obra |
| `/construction/[id]/gantt` | Cronograma Gantt |
| `/construction/[id]/budget` | Orçamento |
| `/construction/[id]/progress` | Progresso Físico |

## APIs Consumidas

### Construção
- `GET /api/v1/construction/projects/` - Lista de projetos
- `GET /api/v1/construction/projects/{id}/` - Detalhe do projeto
- `GET /api/v1/construction/phases/?project={id}` - Fases
- `GET /api/v1/construction/tasks/?project={id}` - Tarefas
- `GET /api/v1/construction/gantt/?project={id}` - Dados Gantt
- `GET /api/v1/construction/stats/` - Estatísticas

### Orçamento
- `GET /api/v1/budget/budgets/?project={id}` - Orçamentos
- `GET /api/v1/budget/budgets/{id}/` - Detalhe
- `GET /api/v1/budget/stats/?project={id}` - Estatísticas

## Design System

### Cores de Status

```typescript
// Projetos/Status
PLANNING:   amber (planeamento)
ACTIVE:     blue (em construção)
ON_HOLD:    amber (em pausa)
COMPLETED:  emerald (concluído)
CANCELLED:  red (cancelado)

// Fases/Tarefas
NOT_STARTED: slate (não iniciado)
IN_PROGRESS: blue (em progresso)
COMPLETED:   emerald (concluído)
DELAYED:     red (atrasado)
```

### Cards

- Border-radius: `rounded-2xl`
- Shadow: `shadow-sm`
- Hover: `hover:shadow-md hover:-translate-y-0.5`

### Tabelas

- Header: `bg-slate-50/50`
- Row hover: `hover:bg-slate-50/70`
- Border: `border-border`

## Responsividade

- **Desktop**: Sidebar fixa (256px) + conteúdo scrollable
- **Tablet**: Layout adaptativo, tabelas com scroll horizontal
- **Mobile**: Não quebra o mobile existente (rota `/mobile/*` separada)

## Dependências

```json
{
  "recharts": "^2.x"
}
```

## Testes

Os componentes incluem estados de loading e error handling:

```typescript
// Loading
<Skeleton className="..." />

// Error
<div className="text-red-600">...</div>

// Empty
<div className="text-muted-foreground">...</div>
```

## Integração

Os hooks usam:
- `useTenant()` - para tenant schema
- `apiClient` - para chamadas API
- TanStack Query - para cache e estado

## Próximos Passos

1. Conectar com APIs reais do backend (A2, A3, A4)
2. Adicionar mutações para criar/editar obras
3. Implementar upload de fotos no progresso
4. Adicionar exportação PDF/Excel do orçamento
5. Criar notificações de atraso/orçamento
