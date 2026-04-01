import { test, expect, TENANT_A } from "./fixtures/auth";

// Helper: login and navigate to CRM
async function loginAndGoToCrm(page: import("@playwright/test").Page) {
    await page.goto("/login");
    await page.fill('[name="email"]', TENANT_A.email);
    await page.fill('[name="password"]', TENANT_A.password);
    await page.click('[type="submit"]');
    await page.waitForURL("/");
    await page.goto("/crm");
}

test.describe("CRM Kanban", () => {
    test.beforeEach(async ({ page }) => {
        await loginAndGoToCrm(page);
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
