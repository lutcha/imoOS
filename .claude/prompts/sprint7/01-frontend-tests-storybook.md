# Sprint 7 — Frontend Tests + Storybook

## Contexto

O frontend Next.js tem E2E Playwright (Sprint 4) mas zero testes de componentes.
Este prompt adiciona:
1. **Vitest + React Testing Library** para testes unitários de componentes
2. **MSW (Mock Service Worker)** para mock de API nos testes
3. **Storybook** para catálogo visual de componentes (design system)
4. **E2E fixes** — corrigir specs Playwright que dependem de serviços em execução

## Pré-requisitos — Ler antes de começar

```
frontend/package.json           → scripts e dependências actuais
frontend/src/components/        → componentes a testar
frontend/tests/e2e/             → specs Playwright existentes
frontend/playwright.config.ts   → config E2E
frontend/src/hooks/             → hooks React Query (para mock de API)
```

```bash
cat frontend/package.json | python -c "import sys,json;d=json.load(sys.stdin);print(json.dumps({'scripts':d['scripts'],'devDependencies':d.get('devDependencies',{})},indent=2))"
ls frontend/src/components/
ls frontend/src/hooks/
```

## Skills a carregar

```
@.claude/skills/14-testing/react-component-testing/SKILL.md
@.claude/skills/14-testing/e2e-playwright/SKILL.md
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `e2e-test-runner` | Verificar e fixar specs Playwright; adicionar specs para contratos e investidor |
| `react-component-builder` | Setup Vitest + MSW; testes dos componentes críticos |

---

## Tarefa 1 — Setup Vitest

Adicionar a `frontend/package.json`:
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage"
  },
  "devDependencies": {
    "vitest": "^1.3.0",
    "@vitest/coverage-v8": "^1.3.0",
    "@vitest/ui": "^1.3.0",
    "@testing-library/react": "^14.2.0",
    "@testing-library/user-event": "^14.5.2",
    "@testing-library/jest-dom": "^6.4.0",
    "msw": "^2.2.0",
    "jsdom": "^24.0.0"
  }
}
```

Criar `frontend/vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/tests/setup.ts'],
    coverage: {
      provider: 'v8',
      thresholds: { branches: 70, functions: 70, lines: 70, statements: 70 },
      include: ['src/components/**', 'src/hooks/**'],
    },
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
});
```

Criar `frontend/src/tests/setup.ts`:
```typescript
import '@testing-library/jest-dom';
import { server } from './mocks/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

---

## Tarefa 2 — MSW mock server

Criar `frontend/src/tests/mocks/handlers.ts`:
```typescript
import { http, HttpResponse } from 'msw';

const DEMO_LEADS = [
  { id: '1', first_name: 'Ana', last_name: 'Costa', email: 'ana@demo.cv',
    status: 'NEW', source: 'WEBSITE', stage: 'LEAD', phone: '+238991234' },
  { id: '2', first_name: 'Pedro', last_name: 'Fonseca', email: 'pedro@demo.cv',
    status: 'CONTACTED', source: 'IMO_CV', stage: 'QUALIFIED', phone: '+238992345' },
];

export const handlers = [
  // Auth
  http.post('/api/auth/login', () =>
    HttpResponse.json({ ok: true }),
  ),

  // CRM Leads
  http.get('/api/v1/crm/leads/', () =>
    HttpResponse.json({ count: 2, results: DEMO_LEADS }),
  ),
  http.patch('/api/v1/crm/leads/:id/', ({ params }) =>
    HttpResponse.json({ ...DEMO_LEADS[0], id: params.id }),
  ),

  // Projects
  http.get('/api/v1/projects/projects/', () =>
    HttpResponse.json({ count: 1, results: [{
      id: 'proj-1', name: 'Residencial Praia Norte', status: 'IN_CONSTRUCTION',
      city: 'Praia', island: 'Santiago',
    }] }),
  ),

  // Contracts
  http.get('/api/v1/contracts/', () =>
    HttpResponse.json({ count: 0, results: [] }),
  ),

  // Tenant usage
  http.get('/api/v1/tenants/usage/', () =>
    HttpResponse.json({
      plan: 'pro',
      projects: { current: 1, limit: 20, pct_used: 5 },
      units: { current: 6, limit: 1000, pct_used: 1 },
      users: { current: 4, limit: 50, pct_used: 8 },
    }),
  ),
];
```

Criar `frontend/src/tests/mocks/server.ts`:
```typescript
import { setupServer } from 'msw/node';
import { handlers } from './handlers';
export const server = setupServer(...handlers);
```

---

## Tarefa 3 — Testes de componentes críticos

**Componentes prioritários a testar:**

### 3a. `useLeads` hook
Criar `frontend/src/hooks/__tests__/useLeads.test.ts`:
```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useLeads } from '../useLeads';

const createWrapper = () => {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) =>
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
};

describe('useLeads', () => {
  it('returns leads list', async () => {
    const { result } = renderHook(() => useLeads({}), { wrapper: createWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.results).toHaveLength(2);
    expect(result.current.data?.results[0].first_name).toBe('Ana');
  });

  it('scopes query key by schema', () => {
    // leadKeys.list sempre inclui o schema para isolamento tenant
    const keys = leadKeys.list('tenant_a', {});
    expect(keys).toContain('tenant_a');
  });
});
```

### 3b. `UnitReservationModal`
Criar `frontend/src/components/crm/__tests__/UnitReservationModal.test.tsx`:
```typescript
// Testar: modal abre, selecção de lead, submissão, feedback de erro
describe('UnitReservationModal', () => {
  it('shows unit details when open', async () => { ... });
  it('requires lead selection', async () => { ... });
  it('requires deposit amount', async () => { ... });
  it('calls createReservation on submit', async () => { ... });
  it('shows error when unit already reserved', async () => { ... });
});
```

### 3c. `Sidebar`
Criar `frontend/src/components/layout/__tests__/Sidebar.test.tsx`:
```typescript
// Testar: links correctos, item activo, links de Contratos e Obra presentes
describe('Sidebar', () => {
  it('renders all navigation links', () => { ... });
  it('highlights active link', () => { ... });
  it('shows upgrade banner when usage >= 80%', () => { ... });
});
```

---

## Tarefa 4 — E2E Playwright: novos specs

Prompt para `e2e-test-runner`:
> "Cria `frontend/tests/e2e/contracts.spec.ts`. Cenários: (1) Admin navega para /contracts — vê listagem vazia com estado correcto; (2) Navega para /projects/[id], tab Unidades — vê botão Reservar em unidade AVAILABLE; (3) Clica Reservar — modal UnitReservationModal abre; (4) Fecha modal — unidade não muda de estado. Usar `loginAndGoTo('/contracts')` helper. Baseado no padrão de `crm-kanban.spec.ts`."

> "Cria `frontend/tests/e2e/investor.spec.ts`. Cenários: (1) Login como investidor (role=investidor) — é redirecionado para /investor/; (2) Admin não pode aceder a /investor/ (redirige para /); (3) /investor/ mostra cards de Portfolio vazio; (4) /investor/documents mostra tabela vazia."

---

## Tarefa 5 — Storybook

```bash
cd frontend && npx storybook@latest init --skip-install
```

Criar stories para componentes críticos:
- `frontend/src/components/crm/LeadCard.stories.tsx`
- `frontend/src/components/layout/Sidebar.stories.tsx`
- `frontend/src/components/ui/StatusBadge.stories.tsx` (badges de estado: Lead, Unidade, Contrato)

Em `package.json`:
```json
"storybook": "storybook dev -p 6006",
"build-storybook": "storybook build"
```

---

## Verificação final

- [ ] `npm test` → Vitest corre sem erros (0 failures)
- [ ] `npm run test:coverage` → ≥ 70% em componentes core
- [ ] MSW intercepta `/api/v1/crm/leads/` nos testes
- [ ] `useLeads.test.ts` passa
- [ ] `UnitReservationModal.test.tsx` passa (5 cenários)
- [ ] `contracts.spec.ts` Playwright passa com servidor em execução
- [ ] `investor.spec.ts` Playwright passa
- [ ] `npm run storybook` → abre em localhost:6006
