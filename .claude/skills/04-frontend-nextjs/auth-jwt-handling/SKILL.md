---
name: auth-jwt-handling
description: JWT auth flow for ImoOS Next.js app — login, httpOnly cookie storage, token refresh, tenant redirect. Auto-load when implementing authentication pages or protecting routes.
argument-hint: [flow] [tenant]
allowed-tools: Read, Write
---

# Auth JWT Handling — ImoOS

## Login Flow
```typescript
// app/auth/login/page.tsx
async function handleLogin(email: string, password: string) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  const { tenant_subdomain } = await response.json();
  // Redirect to tenant subdomain with session established
  window.location.href = `https://${tenant_subdomain}.imos.cv/dashboard`;
}

// app/api/auth/login/route.ts (Next.js API route — sets httpOnly cookie)
export async function POST(request: Request) {
  const { email, password } = await request.json();
  const djangoResp = await fetch(`${process.env.API_URL}/auth/token/`, {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  const { access, refresh, tenant_schema, tenant_name } = await djangoResp.json();

  const response = NextResponse.json({ tenant_subdomain: tenant_schema.replace(/_/g, '-') });
  // httpOnly prevents JS access — XSS protection
  response.cookies.set('access_token', access, { httpOnly: true, secure: true, sameSite: 'strict' });
  response.cookies.set('refresh_token', refresh, { httpOnly: true, secure: true, sameSite: 'strict' });
  return response;
}
```

## Token Refresh
```typescript
// app/api/auth/refresh/route.ts
export async function POST() {
  const cookieStore = cookies();
  const refreshToken = cookieStore.get('refresh_token')?.value;
  if (!refreshToken) return NextResponse.json({ error: 'No refresh token' }, { status: 401 });

  const resp = await fetch(`${process.env.API_URL}/auth/token/refresh/`, {
    method: 'POST',
    body: JSON.stringify({ refresh: refreshToken }),
  });
  const { access } = await resp.json();
  const response = NextResponse.json({ ok: true });
  response.cookies.set('access_token', access, { httpOnly: true, secure: true });
  return response;
}
```

## Key Rules
- JWT stored in httpOnly cookies — never localStorage or sessionStorage
- Access token: 15 min lifetime; auto-refresh in axios interceptor
- On login: always redirect to `{tenant_schema}.imos.cv` — never stay on www.
- On logout: call `/api/auth/logout` to clear cookies AND blacklist refresh token in Django
