# Sprint 1 — Frontend: Auth + API Client + React Query + useProjects()

## Contexto actual

O frontend (`frontend/`) já tem:
- `src/app/layout.tsx` — RootLayout com Sidebar + Topbar
- `src/app/page.tsx` — Dashboard estático (KPI cards + Projetos Recentes)
- `src/components/layout/Sidebar.tsx` + `Topbar.tsx`
- Tailwind + shadcn/ui configurados

O que **não existe** e tens de criar:
- Nenhuma página de login
- Nenhum API client
- Nenhum contexto de auth ou tenant
- Nenhum hook React Query

## Stack disponível no backend

- `POST /api/v1/users/auth/token/` → retorna `{ access, refresh }` (JWT)
- `POST /api/v1/users/auth/token/refresh/` → renova token
- `GET  /api/v1/projects/projects/` → lista projectos do tenant (requer `Authorization: Bearer <token>`)
- JWT contém claims: `tenant_schema`, `user_role`, `email`

## Skills a carregar (por esta ordem)

```
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
@.claude/skills/04-frontend-nextjs/api-client-tenant-header/SKILL.md
@.claude/skills/04-frontend-nextjs/react-query-tenant/SKILL.md
@.claude/skills/04-frontend-nextjs/nextjs-tenant-routing/SKILL.md
@.claude/skills/04-frontend-nextjs/offline-first-pattern/SKILL.md
```

## Agent a activar para componentes

Após criares os hooks e o client, usa o agent para os componentes:
- Agent: `.claude/agents/02-frontend/react-component-builder.md`
- Agent: `.claude/agents/02-frontend/nextjs-tenant-routing.md`

## O que criar (ordem obrigatória)

### 1. `/src/lib/api-client.ts`
Instância axios com:
- `baseURL` a partir de `NEXT_PUBLIC_API_URL`
- Interceptor de request: injeta `Authorization: Bearer <token>` do cookie/localStorage
- Interceptor de response: se 401, tenta refresh → re-envia; se refresh falhar, redireciona para `/login`
- **Seguir exactamente o padrão do skill `api-client-tenant-header`**

### 2. `/src/contexts/AuthContext.tsx`
- `AuthProvider` com `user`, `login(email, password)`, `logout()`, `isAuthenticated`
- Login chama `POST /api/v1/users/auth/token/`, guarda tokens em httpOnly cookies (via API route Next.js) ou `localStorage` como fallback
- Expõe `tenantSchema` e `userRole` extraídos do JWT payload
- **Seguir o padrão do skill `auth-jwt-handling`**

### 3. `/src/contexts/TenantContext.tsx`
- `TenantProvider` com `schema` (extraído do JWT ou do subdomínio)
- Necessário para as query keys do React Query (skill `react-query-tenant`)
- Exemplo de uso: `const { schema } = useTenant()`

### 4. `/src/lib/query-client.ts`
- `QueryClient` configurado com `staleTime: 30_000` por defeito
- **Seguir o padrão do skill `react-query-tenant`** (tenant schema no primeiro nível da key)

### 5. `/src/app/providers.tsx`
- Wrapper com `QueryClientProvider` + `AuthProvider` + `TenantProvider`
- Importado em `app/layout.tsx`

### 6. `/src/hooks/useProjects.ts`
Query key: `['projects', schema]`
- `useProjects(filters?)` — `GET /api/v1/projects/projects/`
- `useProject(id)` — `GET /api/v1/projects/projects/:id/`
- Seguir **exactamente** o padrão do skill `react-query-tenant`

### 7. `/src/app/(auth)/login/page.tsx`
- Form: email + password
- Ao submeter: chama `AuthContext.login()`
- Em caso de erro: mostra mensagem pt-PT
- Em sucesso: redirect para `/`
- Design: centrado, card branco, logo ImoOS, sem Sidebar/Topbar (layout separado)

### 8. `/src/middleware.ts` (Next.js middleware)
- Rotas protegidas: `/` e tudo excepto `/login`
- Se não autenticado → redirect para `/login`
- **Seguir o padrão do skill `nextjs-tenant-routing`**

### 9. Ligar Dashboard a dados reais
Substituir os dados estáticos em `app/page.tsx` pelo hook `useProjects()`:
- "Projetos Recentes" lista os 3 últimos projectos reais
- Adicionar loading skeleton e estado de erro
- KPI "Projetos Activos" usa `data?.count`

## Regras obrigatórias

- NUNCA guardar tokens em `localStorage` sem fallback seguro — preferir cookies httpOnly via API route
- Query keys DEVEM ter `schema` no primeiro elemento (isolamento de cache entre tenants)
- Todos os textos em **pt-PT** (sem inglês no UI)
- Componente `<OfflineIndicator>` do skill `offline-first-pattern` adicionado ao `layout.tsx`

## Verificação final

Antes de marcar como done, confirmar:
- [ ] `npm run build` sem erros TypeScript
- [ ] Login com credenciais válidas redireciona para `/`
- [ ] Login com credenciais inválidas mostra erro em pt-PT
- [ ] Dashboard mostra projectos reais (ou estado vazio elegante)
- [ ] Refresh da página não perde sessão
