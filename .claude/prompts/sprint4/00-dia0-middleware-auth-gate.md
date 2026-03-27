# Sprint 4 — Dia 0 CRÍTICO: `middleware.ts` + Auth Gate

## Contexto

**Prioridade máxima.** Todas as rotas do frontend estão acessíveis publicamente sem login.
Este ficheiro deve ser criado ANTES de qualquer outro trabalho neste sprint.

Confirmado que já existem e funcionam:
- `frontend/src/contexts/AuthContext.tsx` — `restoreSession()` via `/api/auth/refresh`
- `frontend/src/app/api/auth/refresh/route.ts` — extrai `tenant_schema` do JWT payload
- `frontend/src/app/(auth)/login/page.tsx` — layout separado, sem sidebar
- `frontend/src/lib/api-client.ts` — Axios com interceptor de refresh

## Skills a carregar

```
@.claude/skills/04-frontend-nextjs/nextjs-tenant-routing/SKILL.md
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
```

## Agent a activar

- Agent: `nextjs-tenant-routing`
  - Prompt: "Cria `frontend/src/middleware.ts` para ImoOS. Auth via cookie httpOnly `refresh_token`. Rotas públicas: `/auth/*`, `/api/auth/*`, `/api/health`. Rotas protegidas: tudo o resto. Lê o `login/page.tsx` existente antes de editar para adicionar suporte ao param `?next=`."

---

## Tarefa 1 — Criar `frontend/src/middleware.ts`

**Verificar primeiro** que o ficheiro NÃO existe (para não sobrescrever nada):
```bash
ls frontend/src/middleware.ts 2>/dev/null && echo "EXISTE" || echo "NAO EXISTE"
```

**Criar:**
```typescript
import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/auth", "/api/auth", "/api/health"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isPublic = PUBLIC_PATHS.some((p) => pathname.startsWith(p));
  if (isPublic) {
    // Autenticado a tentar aceder ao login → redirecionar para /
    if (pathname.startsWith("/auth/login")) {
      const hasSession = request.cookies.has("refresh_token");
      if (hasSession) {
        return NextResponse.redirect(new URL("/", request.url));
      }
    }
    return NextResponse.next();
  }

  // Rota protegida — verificar cookie de sessão
  const hasSession = request.cookies.has("refresh_token");
  if (!hasSession) {
    const loginUrl = new URL("/auth/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|robots.txt).*)",
  ],
};
```

**Nota de segurança:** O cookie `refresh_token` é apenas indicador de sessão.
A validação real do JWT ocorre no `AuthContext.restoreSession()` no client.
Se o refresh falhar (expirado, revogado), o AuthContext redireciona para `/auth/login`.

---

## Tarefa 2 — Actualizar `frontend/src/app/(auth)/login/page.tsx`

**LER o ficheiro antes de editar.**

Após login bem-sucedido, respeitar o param `?next=`:
```typescript
import { useSearchParams } from "next/navigation";

// Dentro do componente:
const searchParams = useSearchParams();
const next = searchParams.get("next") ?? "/";

// Após login() bem-sucedido:
router.replace(next);
```

---

## Verificação final

- [ ] `GET /inventory` sem cookie → redirect `302` para `/auth/login?next=/inventory`
- [ ] Login → redirect para `/inventory` (destino original preservado)
- [ ] `GET /auth/login` com `refresh_token` cookie → redirect para `/`
- [ ] `GET /api/auth/refresh` sem cookie → retorna `401` (não entra em loop)
- [ ] `npm run build` sem erros TypeScript
- [ ] `npm run lint` sem warnings
