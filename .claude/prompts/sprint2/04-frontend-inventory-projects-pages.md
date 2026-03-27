# Sprint 2 — Frontend: Páginas Inventário + Projectos

## Pré-requisito

- Prompt `03-frontend-middleware-hooks-dashboard.md` concluído
- Hooks `useProjects`, `useUnits`, `useTenant` disponíveis
- `StatusBadge`, `EmptyState`, `LoadingSkeleton` criados

## Estado actual

O Sidebar em `src/components/layout/Sidebar.tsx` já tem links para `/inventory` e `/crm`.
Nenhuma destas rotas tem página — resultam em 404.

## Skills a carregar

```
@.claude/skills/04-frontend-nextjs/react-query-tenant/SKILL.md
@.claude/skills/07-module-inventory/unit-status-workflow/SKILL.md
@.claude/skills/07-module-inventory/unit-pricing-currency/SKILL.md
@.claude/skills/06-module-projects/project-wbs-structure/SKILL.md
@.claude/skills/04-frontend-nextjs/tailwind-design-tokens/SKILL.md
```

## Agents a activar

| Agent | Para que tarefa | Prompt sugerido |
|-------|----------------|-----------------|
| `react-component-builder` | Tabela de unidades, formulário de projecto | "Cria tabela de unidades com filtros de status/tipologia/preço, paginação server-side, e acção de mudar status inline. Usar hook useUnits() e StatusBadge." |
| `tailwind-design-system` | Consistência visual com Dashboard | "Verifica que as páginas novas seguem os mesmos padrões de card, spacing e cores das páginas existentes em layout.tsx e page.tsx" |
| `react-component-builder` | Página de detalhe de projecto | "Cria página de detalhe de projecto com tabs: Visão Geral, Edifícios/Pisos, Unidades, Equipa. Usar useProject(id) e useUnits({project: id})." |

---

## Página 1 — `/inventory` — Tabela de Unidades

**Ficheiro:** `src/app/inventory/page.tsx`

### Layout da página

```
Header: "Inventário de Unidades" | btn "Importar CSV" | btn "Nova Unidade"
──────────────────────────────────────────────────────────────
Filtros (horizontal): Status | Tipologia | Projecto | Preço min-max CVE | [Limpar]
──────────────────────────────────────────────────────────────
Tabela:
  Código | Tipologia | Projecto/Piso | Área (m²) | Preço CVE | Status | Acções
──────────────────────────────────────────────────────────────
Paginação: "Mostrando 1-20 de 485 unidades" | < 1 2 3 ... >
```

### Requisitos técnicos

**Filtros:**
```typescript
// Estado local para filtros — sincronizar com URL (useSearchParams)
const [filters, setFilters] = useState({
  status: '',
  unit_type: '',
  project: '',         // floor__building__project
  price_cve_min: '',
  price_cve_max: '',
  page: 1,
});

// Passar para o hook
const { data, isLoading } = useUnits(filters);
```

**Paginação server-side:** usar o `count` e `next`/`previous` da resposta DRF paginada.

**Tabela de status com cores:**
- AVAILABLE → badge verde `bg-emerald-50 text-emerald-700`
- RESERVED → badge amarelo `bg-amber-50 text-amber-700`
- CONTRACT → badge azul `bg-blue-50 text-blue-700`
- SOLD → badge cinza `bg-slate-100 text-slate-600`
- MAINTENANCE → badge laranja `bg-orange-50 text-orange-700`

**Acção inline "Mudar Status":**
```typescript
// Dropdown inline na coluna de status — usar useUpdateUnitStatus() do skill react-query-tenant
// Confirmar antes de mudar para SOLD (modal de confirmação)
```

**Formatação de preço CVE:**
```typescript
// Usar Intl.NumberFormat para formatar preços em CVE
const formatCVE = (value: string | number) =>
  new Intl.NumberFormat('pt-CV', { style: 'currency', currency: 'CVE' })
    .format(Number(value));
```

**Botão "Importar CSV":**
- Abre modal com input de ficheiro
- Submit faz `POST /api/v1/inventory/units/import-csv/`
- Mostra task_id e polling do status (ou mensagem "a processar em background")

---

## Página 2 — `/projects` — Lista de Projectos

**Ficheiro:** `src/app/projects/page.tsx`

### Layout da página

```
Header: "Projectos" | btn "Novo Projecto"
──────────────────────────────────────────
Grid de cards (3 cols):
  [Card Projecto: nome, cidade, status badge, X unidades, X% vendido, data entrega]
──────────────────────────────────────────
Estado vazio: "Ainda sem projectos. Crie o primeiro." + CTA
```

**Card de projecto:**
```typescript
interface ProjectCardProps {
  project: Project;
}

// Card com:
// - Header: nome + status badge
// - Subinfo: cidade, data de entrega estimada
// - Progressbar: % unidades vendidas (sold/total_units)
// - Footer: "X Edifícios · Y Unidades · Ver detalhes →"
```

---

## Página 3 — `/projects/[id]` — Detalhe do Projecto

**Ficheiro:** `src/app/projects/[id]/page.tsx`

### Layout com tabs

```
Breadcrumb: Projectos > Cape View Residencial
Header: Nome | Status Badge | "Editar" btn
──────────────────────────────────────────
Tabs: [Visão Geral] [Unidades] [Edifícios] [Documentos]
──────────────────────────────────────────
Tab "Visão Geral":
  KPIs: Total unidades | Disponíveis | Reservadas | Vendidas
  Mapa (placeholder para Mapbox/Leaflet — Sprint 3)
  Info: localização, área total, data início, data entrega

Tab "Unidades":
  Tabela filtrada por projecto — reusar componente de /inventory
  filtros: status, tipologia, piso

Tab "Edifícios":
  Lista de edifícios com accordion → pisos → unidades (visão estrutural)
```

**Fetch de dados:**
```typescript
const { id } = useParams();
const { data: project } = useProject(id as string);
const { data: units } = useUnits({ 'floor__building__project': id as string });
```

---

## Página 4 — `/crm` — Pipeline de Leads (scaffold)

**Ficheiro:** `src/app/crm/page.tsx` — apenas scaffold para Sprint 2, Kanban completo no Sprint 3

```typescript
// Sprint 2: só a lista de leads com filtros básicos
// Sprint 3: transformar em Kanban drag-and-drop
// Não implementar o Kanban agora — YAGNI
```

**Layout simples para Sprint 2:**
```
Header: "CRM — Pipeline de Vendas" | btn "Novo Lead"
──────────────────────────────────────────
Filtros: Status | Fonte | Vendedor assignado
──────────────────────────────────────────
Lista de leads com cards simples
```

---

## Actualizações no Sidebar

**Ficheiro:** `src/components/layout/Sidebar.tsx` — ler antes de editar.

Adicionar o item "Projectos" que falta no menu (actualmente só tem "Inventário"):
```typescript
const menuItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/" },
  { icon: Building2, label: "Projectos", href: "/projects" },     // ← adicionar
  { icon: Home, label: "Inventário", href: "/inventory" },
  { icon: Users, label: "CRM", href: "/crm" },
  { icon: Wallet, label: "Financeiro", href: "/finance" },
  { icon: Settings, label: "Configurações", href: "/settings" },
];
```

---

## Verificação final

- [ ] `GET /inventory` carrega tabela de unidades (ou empty state elegante)
- [ ] Filtros de status e preço actualizam a tabela sem reload
- [ ] Preços formatados em CVE: `1.234.567 CVE` (não `1234567`)
- [ ] `GET /projects` carrega grid de projectos
- [ ] `GET /projects/{id}` carrega detalhe com tabs funcionais
- [ ] `GET /crm` carrega lista de leads
- [ ] Sidebar activo destaca a rota correcta em todas as páginas
- [ ] `npm run build` sem erros TypeScript
- [ ] Todas as páginas têm loading skeleton e empty state
