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
