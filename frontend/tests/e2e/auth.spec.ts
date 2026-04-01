import { test, expect, TENANT_A } from "./fixtures/auth";

test.describe("Auth Flow", () => {
    test("redireciona para login quando não autenticado", async ({ page }) => {
        await page.goto("/inventory");
        // middleware.ts redireciona para /login?next=... (não /auth/login — (auth) é grupo de layout)
        await expect(page).toHaveURL(/\/login\?next=\/inventory/);
    });

    test("login bem-sucedido redireciona para destino original", async ({ page }) => {
        await page.goto("/inventory");
        await expect(page).toHaveURL(/\/login/);
        await page.fill('[name="email"]', TENANT_A.email);
        await page.fill('[name="password"]', TENANT_A.password);
        await page.click('[type="submit"]');
        await expect(page).toHaveURL("/inventory");
    });

    test("já autenticado aceder a /login → redireciona para /", async ({ page }) => {
        // Login primeiro
        await page.goto("/login");
        await page.fill('[name="email"]', TENANT_A.email);
        await page.fill('[name="password"]', TENANT_A.password);
        await page.click('[type="submit"]');
        await page.waitForURL("/");

        // Tentar aceder ao login novamente — middleware redireciona para /
        await page.goto("/login");
        await expect(page).toHaveURL("/");
    });

    test("logout limpa sessão e redireciona para login", async ({ page }) => {
        // Login
        await page.goto("/login");
        await page.fill('[name="email"]', TENANT_A.email);
        await page.fill('[name="password"]', TENANT_A.password);
        await page.click('[type="submit"]');
        await page.waitForURL("/");

        // Abrir user menu e clicar em logout
        await page.click('[data-testid="user-menu"]');
        await page.click('[data-testid="logout-btn"]');
        await expect(page).toHaveURL(/\/login/);

        // Confirmar que rota protegida não é mais acessível
        await page.goto("/crm");
        await expect(page).toHaveURL(/\/login/);
    });
});
