---
name: accessibility-wcag-check
description: axe-core em testes Playwright para verificar violações WCAG 2.1 AA em cada página, teste de navegação por teclado e gestão de foco em modais.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Garantir que o ImoOS cumpre os requisitos WCAG 2.1 AA de acessibilidade. Os testes automatizados com axe-core detetam violações comuns e os testes de teclado validam a navegabilidade sem rato.

## Code Pattern

```typescript
// e2e/tests/accessibility.spec.ts
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const PAGES_TO_CHECK = [
  { path: "/login/", name: "Página de Login" },
  { path: "/dashboard/", name: "Dashboard" },
  { path: "/dashboard/projects/", name: "Lista de Projetos" },
  { path: "/dashboard/inventory/units/", name: "Inventário de Unidades" },
  { path: "/dashboard/crm/leads/", name: "CRM - Leads" },
];

test.describe("WCAG 2.1 AA — Verificação Automática", () => {
  for (const page_info of PAGES_TO_CHECK) {
    test(`${page_info.name} não tem violações WCAG`, async ({ page }) => {
      await page.goto(page_info.path);
      await page.waitForLoadState("networkidle");

      const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
        .exclude(".skip-accessibility")  // excluir componentes de terceiros conhecidos
        .analyze();

      // Reportar violações de forma legível
      if (results.violations.length > 0) {
        const report = results.violations.map(v =>
          `[${v.impact?.toUpperCase()}] ${v.id}: ${v.description}\n  Afeta: ${v.nodes.map(n => n.html).join("\n  ")}`
        ).join("\n\n");
        console.log(`Violações em ${page_info.name}:\n${report}`);
      }

      expect(results.violations).toHaveLength(0);
    });
  }
});

test.describe("Navegação por Teclado", () => {
  test("formulário de login navegável por teclado", async ({ page }) => {
    await page.goto("/login/");

    // Tab para o campo email
    await page.keyboard.press("Tab");
    await expect(page.getByLabel("Email")).toBeFocused();

    // Tab para a palavra-passe
    await page.keyboard.press("Tab");
    await expect(page.getByLabel("Palavra-passe")).toBeFocused();

    // Tab para o botão de submit
    await page.keyboard.press("Tab");
    await expect(page.getByRole("button", { name: /Entrar/i })).toBeFocused();

    // Enter para submeter
    await page.keyboard.press("Enter");
  });

  test("modal de criação de projeto — gestão de foco", async ({ page }) => {
    await loginAsTenantUser(page);
    await page.goto("/dashboard/projects/");

    // Abrir modal
    await page.getByRole("button", { name: /Novo Projeto/i }).click();
    const modal = page.getByRole("dialog");
    await expect(modal).toBeVisible();

    // Verificar que o foco foi para dentro do modal
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(["INPUT", "BUTTON", "TEXTAREA", "SELECT"]).toContain(focusedElement);

    // Fechar modal com Escape
    await page.keyboard.press("Escape");
    await expect(modal).not.toBeVisible();

    // Verificar que o foco voltou ao botão que abriu o modal
    await expect(page.getByRole("button", { name: /Novo Projeto/i })).toBeFocused();
  });
});
```

```typescript
// e2e/helpers/accessibility.ts — helper reutilizável
import AxeBuilder from "@axe-core/playwright";
import { Page } from "@playwright/test";

export async function checkPageAccessibility(page: Page, options?: {
  exclude?: string[];
  tags?: string[];
}) {
  const builder = new AxeBuilder({ page })
    .withTags(options?.tags ?? ["wcag2a", "wcag2aa", "wcag21aa"]);

  for (const selector of options?.exclude ?? []) {
    builder.exclude(selector);
  }

  return builder.analyze();
}
```

## Key Rules

- Verificar WCAG 2.1 AA (não apenas 2.0) — incluir tags `wcag21a` e `wcag21aa` no axe-core.
- Testar gestão de foco em modais: foco deve entrar no modal ao abrir e regressar ao trigger ao fechar.
- Excluir componentes de terceiros com seletores CSS para evitar falsos positivos não accionáveis.
- Executar os testes de acessibilidade em CI para bloquear PRs com regressões de acessibilidade.

## Anti-Pattern

```typescript
// ERRADO: verificar acessibilidade apenas visualmente durante review de PR
// Os testes automatizados com axe-core detetam ~57% das violações WCAG — complementar mas não substituir
```
