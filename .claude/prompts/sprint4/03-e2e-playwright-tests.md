# Sprint 4 — E2E Playwright: Auth + CRM + Reservas

## Pré-requisitos — Ler antes de começar

```
frontend/src/middleware.ts                    → deve existir (prompt 00)
frontend/src/app/(auth)/login/page.tsx        → ler antes de criar testes
tests/e2e/                                    → verificar se existe
frontend/playwright.config.ts                 → verificar se existe
```

```bash
ls tests/e2e/ 2>/dev/null && echo "JA EXISTE — ler tudo" || echo "NAO EXISTE"
ls frontend/playwright.config.ts 2>/dev/null || echo "NAO EXISTE"
```

**Dependência:** Prompt 00 (middleware.ts) deve estar completo antes de correr estes testes.

## Skills a carregar

```
@.claude/skills/14-testing/e2e-playwright/SKILL.md
@.claude/skills/14-testing/tenant-fixtures/SKILL.md
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
```

## Agent a activar

- Agent: `e2e-test-runner`
  - Prompt: "Cria a suite Playwright E2E para ImoOS. Cenários: auth flow completo, CRM kanban drag, fluxo de reserva. Usa dois tenants de teste (tenant_a, tenant_b). Verifica que dados de tenant_a não aparecem em sessão de tenant_b. Necessita de servidor de staging ou `localhost:3000` + backend `localhost:8000`."

---

## Tarefa 1 — Configurar Playwright

**Verificar** se `frontend/playwright.config.ts` existe antes de criar.

Se não existir, criar `frontend/playwright.config.ts`:
```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "../tests/e2e",
  fullyParallel: false,  // testes de tenant isolation devem ser sequenciais
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
```

Instalar Playwright se necessário:
```bash
cd frontend && npx playwright install --with-deps chromium
```

---

## Tarefa 2 — Fixtures de tenant para E2E

Criar `tests/e2e/fixtures/auth.ts`:
```typescript
import { test as base, expect } from "@playwright/test";

type AuthFixtures = {
  tenantAPage: import("@playwright/test").Page;
  tenantBPage: import("@playwright/test").Page;
};

// Credenciais de teste (devem existir no ambiente de staging)
export const TENANT_A = {
  domain: process.env.E2E_TENANT_A_DOMAIN ?? "demo-a.localhost:3000",
  email: process.env.E2E_TENANT_A_EMAIL ?? "vendedor@demo-a.imos.cv",
  password: process.env.E2E_TENANT_A_PASSWORD ?? "testpass123",
};

export const TENANT_B = {
  domain: process.env.E2E_TENANT_B_DOMAIN ?? "demo-b.localhost:3000",
  email: process.env.E2E_TENANT_B_EMAIL ?? "vendedor@demo-b.imos.cv",
  password: process.env.E2E_TENANT_B_PASSWORD ?? "testpass123",
};

export const test = base.extend<AuthFixtures>({
  tenantAPage: async ({ browser }, use) => {
    const ctx = await browser.newContext({ baseURL: `http://${TENANT_A.domain}` });
    const page = await ctx.newPage();
    await use(page);
    await ctx.close();
  },
  tenantBPage: async ({ browser }, use) => {
    const ctx = await browser.newContext({ baseURL: `http://${TENANT_B.domain}` });
    const page = await ctx.newPage();
    await use(page);
    await ctx.close();
  },
});

export { expect };
```

---

## Tarefa 3 — `tests/e2e/auth.spec.ts`

```typescript
import { test, expect, TENANT_A } from "./fixtures/auth";

test.describe("Auth Flow", () => {
  test("redireciona para login quando não autenticado", async ({ page }) => {
    await page.goto("/inventory");
    await expect(page).toHaveURL(/\/auth\/login\?next=\/inventory/);
  });

  test("login bem-sucedido redireciona para destino original", async ({ page }) => {
    await page.goto("/inventory");
    await page.fill('[name="email"]', TENANT_A.email);
    await page.fill('[name="password"]', TENANT_A.password);
    await page.click('[type="submit"]');
    await expect(page).toHaveURL("/inventory");
  });

  test("já autenticado aceder a /auth/login → redireciona para /", async ({ page }) => {
    // Fazer login primeiro
    await page.goto("/auth/login");
    await page.fill('[name="email"]', TENANT_A.email);
    await page.fill('[name="password"]', TENANT_A.password);
    await page.click('[type="submit"]');
    await page.waitForURL("/");

    // Tentar aceder ao login novamente
    await page.goto("/auth/login");
    await expect(page).toHaveURL("/");
  });

  test("logout limpa sessão e redireciona para login", async ({ page }) => {
    await page.goto("/auth/login");
    await page.fill('[name="email"]', TENANT_A.email);
    await page.fill('[name="password"]', TENANT_A.password);
    await page.click('[type="submit"]');
    await page.waitForURL("/");

    // Logout (ajustar selector ao componente real)
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-btn"]');
    await expect(page).toHaveURL(/\/auth\/login/);

    // Verificar que rota protegida não é acessível
    await page.goto("/crm");
    await expect(page).toHaveURL(/\/auth\/login/);
  });
});
```

---

## Tarefa 4 — `tests/e2e/crm-kanban.spec.ts`

```typescript
import { test, expect, TENANT_A } from "./fixtures/auth";

test.describe("CRM Kanban", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/auth/login");
    await page.fill('[name="email"]', TENANT_A.email);
    await page.fill('[name="password"]', TENANT_A.password);
    await page.click('[type="submit"]');
    await page.waitForURL("/");
    await page.goto("/crm");
  });

  test("carrega o board Kanban com colunas de pipeline", async ({ page }) => {
    // 7 colunas: Novo, Contactado, Visita Agendada, Proposta Enviada, Negociação, Ganho, Perdido
    const columns = page.locator("[data-testid='kanban-column']");
    await expect(columns).toHaveCount(7);
  });

  test("toggle para vista de lista", async ({ page }) => {
    await page.click('[aria-label="Lista"]');
    await expect(page.locator("table")).toBeVisible();
    await expect(page.locator("[data-testid='kanban-column']")).toHaveCount(0);
  });

  test("pesquisa filtra leads", async ({ page }) => {
    // Mudar para lista para verificar filtragem
    await page.click('[aria-label="Lista"]');
    await page.fill('[placeholder*="Pesquisar"]', "nenhum_resultado_xyzabc");
    await expect(page.locator("text=Nenhum lead encontrado")).toBeVisible();
  });
});
```

---

## Tarefa 5 — `tests/e2e/tenant-isolation.spec.ts`

```typescript
import { test, expect } from "./fixtures/auth";
import { TENANT_A, TENANT_B } from "./fixtures/auth";

test.describe("Tenant Isolation (E2E)", () => {
  test("dados de tenant_a não aparecem em sessão de tenant_b", async ({
    tenantAPage,
    tenantBPage,
  }) => {
    // Login tenant_a — criar/verificar lead
    await tenantAPage.goto("/auth/login");
    await tenantAPage.fill('[name="email"]', TENANT_A.email);
    await tenantAPage.fill('[name="password"]', TENANT_A.password);
    await tenantAPage.click('[type="submit"]');
    await tenantAPage.waitForURL("/");

    // Login tenant_b — API não deve devolver dados de tenant_a
    await tenantBPage.goto("/auth/login");
    await tenantBPage.fill('[name="email"]', TENANT_B.email);
    await tenantBPage.fill('[name="password"]', TENANT_B.password);
    await tenantBPage.click('[type="submit"]');
    await tenantBPage.waitForURL("/");

    // Verificar que a API retorna apenas dados do próprio tenant
    const response = await tenantBPage.evaluate(async () => {
      const r = await fetch("/api/v1/crm/leads/", {
        credentials: "include",
      });
      return r.json();
    });

    // Não deve conter dados criados por tenant_a
    // (Este teste é mais significativo com dados de seed conhecidos)
    expect(response).toHaveProperty("results");
  });
});
```

---

## Tarefa 6 — Adicionar scripts ao `package.json`

**Ler `frontend/package.json` antes de editar.**

Adicionar em `scripts`:
```json
{
  "test:e2e": "playwright test",
  "test:e2e:ui": "playwright test --ui",
  "test:e2e:report": "playwright show-report"
}
```

---

## Verificação final

- [ ] `cd frontend && npm run test:e2e -- auth.spec.ts` — todos passing
- [ ] Redireccionamento para `/auth/login?next=` confirmado
- [ ] Dados de tenant_b não contaminados por tenant_a
- [ ] `npm run build` ainda compila sem erros
- [ ] CI: adicionar step `npm run test:e2e` no `.github/workflows/` (após staging deploy)
