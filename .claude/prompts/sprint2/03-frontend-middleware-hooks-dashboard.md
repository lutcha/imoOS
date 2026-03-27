# Sprint 2 — Frontend: Middleware + Hooks de dados + Dashboard real

## Estado actual (verificado)

**Existe e está correcto:**
- `src/lib/api-client.ts` — axios com interceptors JWT + refresh ✓
- `src/contexts/AuthContext.tsx` — login, logout, session restore ✓
- `src/contexts/TenantContext.tsx` — deriva de AuthContext ✓
- `src/providers/Providers.tsx` — QueryClient + Auth + Tenant ✓
- `src/app/(auth)/login/page.tsx` — form de login ✓
- `src/app/api/auth/{login,refresh,logout}/route.ts` ✓ (URLs corrigidas no bug-0)

**Não existe ainda:**
- `src/middleware.ts` — rotas desprotegidas
- Nenhum hook React Query real (useProjects, useUnits, etc.)
- Dashboard com dados reais — ainda estático
- `src/hooks/` — directório vazio

## Skills a carregar

```
@.claude/skills/04-frontend-nextjs/react-query-tenant/SKILL.md
@.claude/skills/04-frontend-nextjs/nextjs-tenant-routing/SKILL.md
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
@.claude/skills/04-frontend-nextjs/offline-first-pattern/SKILL.md
@.claude/skills/00-global/coding-standards/SKILL.md
```

## Agents a activar

| Agent | Para que tarefa |
|-------|----------------|
| `nextjs-tenant-routing` | Criar `middleware.ts` com protecção de rotas e detecção de subdomain |
| `react-component-builder` | Converter Dashboard estático em componentes com loading states |
| `tailwind-design-system` | Loading skeletons, estados de erro e de vazio consistentes com design actual |

---

## Tarefa 1 — `src/middleware.ts` (protecção de rotas)

```typescript
/**
 * Next.js Middleware — protege rotas autenticadas.
 * Skill: nextjs-tenant-routing + auth-jwt-handling
 *
 * Lógica:
 * - Rotas públicas: /auth/login, /api/auth/*
 * - Todas as outras requerem refresh_token cookie válido
 * - Se não autenticado → redirect /auth/login com returnUrl
 */
import { NextRequest, NextResponse } from 'next/server';

const PUBLIC_PATHS = ['/auth/login', '/api/auth'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isPublic = PUBLIC_PATHS.some(p => pathname.startsWith(p));
  if (isPublic) return NextResponse.next();

  const hasRefreshToken = request.cookies.has('refresh_token');
  if (!hasRefreshToken) {
    const loginUrl = new URL('/auth/login', request.url);
    loginUrl.searchParams.set('returnUrl', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.png).*)'],
};
```

**Após criar:** verificar que `/` sem cookie redireciona para `/auth/login`.

---

## Tarefa 2 — `src/hooks/` — hooks React Query

Criar um ficheiro por domínio. Seguir **exactamente** o padrão de query keys do skill `react-query-tenant`:
- Primeiro elemento da key: `schema` (do `useTenant()`)
- `staleTime` ajustado à sensibilidade dos dados

### `src/hooks/useProjects.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTenant } from '@/contexts/TenantContext';
import apiClient from '@/lib/api-client';

// Tipos alinhados com apps/projects/models.py
export interface Project {
  id: string;
  name: string;
  slug: string;
  status: 'PLANNING' | 'APPROVED' | 'IN_CONSTRUCTION' | 'COMPLETED' | 'PAUSED';
  city: string;
  address: string;
  description: string;
  total_units: number;
  created_at: string;
}

const keys = {
  all: (schema: string) => ['projects', schema] as const,
  detail: (schema: string, id: string) => ['projects', schema, id] as const,
};

export function useProjects(filters: Record<string, string> = {}) {
  const { schema } = useTenant();
  return useQuery({
    queryKey: [...keys.all(schema), filters],
    queryFn: () => apiClient.get('/projects/projects/', { params: filters }).then(r => r.data),
    staleTime: 60_000,  // projectos mudam pouco — 60s
  });
}

export function useProject(id: string) {
  const { schema } = useTenant();
  return useQuery({
    queryKey: keys.detail(schema, id),
    queryFn: () => apiClient.get(`/projects/projects/${id}/`).then(r => r.data),
    enabled: !!id,
  });
}
```

### `src/hooks/useUnits.ts`

```typescript
// Tipos alinhados com apps/inventory/models.py
export interface Unit {
  id: string;
  code: string;
  status: 'AVAILABLE' | 'RESERVED' | 'CONTRACT' | 'SOLD' | 'MAINTENANCE';
  status_display: string;
  area_bruta: string;
  area_util: string | null;
  orientation: string;
  unit_type_detail: { id: string; name: string; code: string };
  pricing: {
    price_cve: string;
    price_eur: string | null;
    final_price_cve: string;
    discount_type: string;
  } | null;
}

// staleTime: 5_000 — status muda frequentemente (reservas, vendas)
// Filtros: status, unit_type, floor__building__project, price_cve_min, price_cve_max
```

### `src/hooks/useLeads.ts`

```typescript
// Tipos alinhados com apps/crm/models.py
// staleTime: 10_000 — leads mudam com frequência
// Incluir action pipeline: GET /crm/leads/pipeline/
export function useLeadsPipeline() { ... }
```

### `src/hooks/useTenantStats.ts`

```typescript
// GET /api/v1/tenant/usage/ → { projects_count, units_count, users_count, plan_limits }
// Usado pelo Dashboard para KPIs reais
// staleTime: 30_000
```

---

## Tarefa 3 — Dashboard com dados reais

**Ficheiro:** `src/app/page.tsx` — ler antes de editar.

Substituir os dados hardcoded do array `stats` por dados reais dos hooks:

```typescript
// Substituir:
const stats = [
  { label: "Projetos Ativos", value: "12", ... },
  ...
]

// Por:
const { data: tenantStats, isLoading: statsLoading } = useTenantStats();
const { data: projectsData } = useProjects({ status: 'IN_CONSTRUCTION' });
```

**Estados a implementar:**
1. **Loading:** skeleton cards (usar `animate-pulse` do Tailwind) — manter dimensões actuais dos cards
2. **Erro:** mensagem discreta com botão "Tentar novamente"
3. **Vazio:** texto "Ainda sem dados — crie o primeiro projecto" com CTA

**"Projetos Recentes":** substituir os 3 items hardcoded por `projectsData?.results.slice(0, 3)`.

**Componente `<OfflineIndicator>` do skill `offline-first-pattern`:**
Adicionar ao `src/app/layout.tsx` acima do `<main>`.

---

## Tarefa 4 — `src/components/ui/` — componentes partilhados

Antes de criar páginas novas, criar estes componentes base que serão reutilizados:

**`src/components/ui/StatusBadge.tsx`**
```typescript
// Badge colorido para status de unidades e leads
// AVAILABLE → verde, RESERVED → amarelo, SOLD → cinza, CONTRACT → azul, MAINTENANCE → laranja
// Seguir cores do tailwind-design-system — não inventar cores novas
```

**`src/components/ui/EmptyState.tsx`**
```typescript
// Estado de lista vazia reutilizável
// Props: icon, title, description, actionLabel?, onAction?
```

**`src/components/ui/LoadingSkeleton.tsx`**
```typescript
// Skeleton genérico para cards e tabelas
// Props: rows?, cols?, className?
```

---

## Verificação final

- [ ] Aceder a `/` sem cookie → redirect automático para `/auth/login`
- [ ] Após login → redirect para `/` com dados reais do dashboard
- [ ] Dashboard mostra loading skeleton enquanto API não responde
- [ ] Dashboard mostra projectos reais em "Projetos Recentes"
- [ ] KPI "Projetos Ativos" usa dado real de `useTenantStats()`
- [ ] `<OfflineIndicator>` aparece quando simulado offline (DevTools → Network → Offline)
- [ ] `npm run build` sem erros TypeScript
