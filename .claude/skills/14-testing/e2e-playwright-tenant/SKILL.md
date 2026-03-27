---
name: e2e-playwright-tenant
description: Teste Playwright que autentica como utilizador de inquilino, navega para projetos, cria projeto e verifica que aparece na lista. Corre contra URL de staging.
argument-hint: "[tenant_slug]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Validar os fluxos críticos de utilizador de ponta a ponta contra o ambiente de staging. O teste garante que a autenticação multi-tenant, navegação e criação de projetos funcionam corretamente após cada deploy.

## Code Pattern

```typescript
// e2e/tests/tenant-project-flow.spec.ts
import { test, expect, Page } from "@playwright/test";

const STAGING_URL = process.env.STAGING_URL || "https://demo.imoos.cv";
const TENANT_EMAIL = process.env.TEST_TENANT_EMAIL || "test@demo.imoos.cv";
const TENANT_PASSWORD = process.env.TEST_TENANT_PASSWORD || "";

test.describe("Fluxo de Projeto de Inquilino", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsTenantUser(page);
  });

  test("criar projeto e verificar na lista", async ({ page }) => {
    // 1. Navegar para a secção de projetos
    await page.goto(`${STAGING_URL}/dashboard/projects/`);
    await expect(page).toHaveTitle(/Projetos/);

    // 2. Clicar em "Novo Projeto"
    await page.getByRole("button", { name: /Novo Projeto/i }).click();
    await expect(page.getByRole("dialog")).toBeVisible();

    // 3. Preencher o formulário
    const projectName = `Projeto Teste E2E ${Date.now()}`;
    await page.getByLabel("Nome do Projeto").fill(projectName);
    await page.getByLabel("Ilha").selectOption("Santiago");
    await page.getByLabel("Data de Início").fill("2025-01-01");

    // 4. Submeter
    await page.getByRole("button", { name: /Criar Projeto/i }).click();

    // 5. Verificar mensagem de sucesso
    await expect(page.getByText(/Projeto criado com sucesso/i)).toBeVisible({ timeout: 5000 });

    // 6. Verificar que aparece na lista
    await page.goto(`${STAGING_URL}/dashboard/projects/`);
    await expect(page.getByText(projectName)).toBeVisible();
  });

  test("isolamento: não ver projetos de outros inquilinos", async ({ page }) => {
    await page.goto(`${STAGING_URL}/dashboard/projects/`);
    // Garantir que apenas projetos do inquilino "demo" aparecem
    const response = await page.request.get(`${STAGING_URL}/api/v1/projects/`);
    const data = await response.json();
    for (const project of data.results) {
      expect(project.tenant_schema).toBe("demo");
    }
  });
});

async function loginAsTenantUser(page: Page) {
  await page.goto(`${STAGING_URL}/login/`);
  await page.getByLabel("Email").fill(TENANT_EMAIL);
  await page.getByLabel("Palavra-passe").fill(TENANT_PASSWORD);
  await page.getByRole("button", { name: /Entrar/i }).click();
  await expect(page).toHaveURL(/dashboard/, { timeout: 10000 });
}
```

```typescript
// playwright.config.ts
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e/tests",
  use: {
    baseURL: process.env.STAGING_URL || "https://demo.imoos.cv",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "on-first-retry",
  },
  retries: process.env.CI ? 2 : 0,
  reporter: [["html", { outputFolder: "e2e/reports" }]],
});
```

```yaml
# .github/workflows/e2e.yml
- name: Run E2E Tests
  run: npx playwright test
  env:
    STAGING_URL: ${{ secrets.STAGING_URL }}
    TEST_TENANT_EMAIL: ${{ secrets.TEST_TENANT_EMAIL }}
    TEST_TENANT_PASSWORD: ${{ secrets.TEST_TENANT_PASSWORD }}
```

## Key Rules

- Usar nomes únicos por execução (`Date.now()`) para evitar conflitos entre corridas paralelas.
- As credenciais de teste devem vir de variáveis de ambiente — nunca hardcoded no código.
- Incluir um teste de isolamento de inquilino para verificar que não há fuga de dados entre schemas.
- Configurar `retries: 2` em CI para lidar com flakiness de rede no ambiente de staging.

## Anti-Pattern

```typescript
// ERRADO: usar seletores CSS frágeis em vez de roles semânticos
await page.click(".btn-primary");  // quebra com qualquer mudança de CSS
await page.getByRole("button", { name: "Criar" })  // robusto — baseado em semântica
```
