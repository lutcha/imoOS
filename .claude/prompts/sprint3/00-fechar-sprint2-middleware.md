# Sprint 2 Closer — `middleware.ts` (dívida crítica)

## Contexto

Este ficheiro é o único item em falta do Sprint 2.
Sem ele, **todas as rotas autenticadas estão publicamente acessíveis** — qualquer URL funciona sem login.

O `AuthContext.tsx` e o `TenantContext.tsx` já existem e funcionam.
O `frontend/src/app/(auth)/login/page.tsx` já existe com layout separado.
O `frontend/src/app/api/auth/refresh/route.ts` já existe (session restore via cookie).

## Skills a carregar

```
@.claude/skills/04-frontend-nextjs/nextjs-tenant-routing/SKILL.md
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
```

## Agent a activar

- Agent: `.claude/agents/02-frontend/nextjs-tenant-routing.md`
  - Prompt: "Cria o `middleware.ts` para ImoOS. O auth usa JWT em memória restaurado via httpOnly cookie num route handler `/api/auth/refresh`. O middleware não tem acesso directo ao token em memória — tem de inferir a sessão pelo cookie `refresh_token`."

## Ficheiro a criar: `frontend/src/middleware.ts`

**Lógica:**

1. Rotas públicas (sem auth): `/auth/*`, `/api/auth/*`
2. Rotas protegidas: tudo o resto (`/`, `/projects`, `/inventory`, `/crm`, `/settings`, etc.)
3. Para determinar se há sessão activa: verificar a existência do cookie `refresh_token`
   - Cookie presente → deixar passar (o `AuthContext` valida o token real no client)
   - Cookie ausente → redirect para `/auth/login`
4. Se já autenticado e aceder a `/auth/login` → redirect para `/`

```typescript
import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/auth", "/api/auth", "/api/health"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow all public paths
  const isPublic = PUBLIC_PATHS.some((p) => pathname.startsWith(p));
  if (isPublic) {
    // If authenticated, don't show login page again
    if (pathname.startsWith("/auth/login")) {
      const hasSession = request.cookies.has("refresh_token");
      if (hasSession) {
        return NextResponse.redirect(new URL("/", request.url));
      }
    }
    return NextResponse.next();
  }

  // Protected route — check for session cookie
  const hasSession = request.cookies.has("refresh_token");
  if (!hasSession) {
    const loginUrl = new URL("/auth/login", request.url);
    loginUrl.searchParams.set("next", pathname); // preserve intended destination
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    // Match everything except _next internals and static files
    "/((?!_next/static|_next/image|favicon.ico|robots.txt).*)",
  ],
};
```

**Nota importante:** O middleware usa o cookie `refresh_token` apenas como indicador de sessão.
A validação real do JWT acontece no `AuthContext.restoreSession()` no client.
Se o refresh falhar (token expirado, revogado), o AuthContext redireciona para `/auth/login` — dupla protecção.

## Actualizar login page para usar `next` param

**Ficheiro:** `frontend/src/app/(auth)/login/page.tsx` — ler antes de editar.

Após login bem-sucedido, usar o param `next` se existir:
```typescript
import { useSearchParams } from "next/navigation";

const searchParams = useSearchParams();
const next = searchParams.get("next") ?? "/";

// Na função handleSubmit, após login():
router.replace(next);
```

## Verificação final

- [ ] Aceder a `/inventory` sem login → redirect para `/auth/login?next=/inventory`
- [ ] Login bem-sucedido → redirect para `/inventory` (destino original)
- [ ] Aceder a `/auth/login` com sessão activa → redirect para `/`
- [ ] `/api/auth/refresh` continua acessível sem auth (é chamado pelo middleware do client)
- [ ] `npm run build` sem erros TypeScript
