---
name: nextjs-tenant-routing
description: Next.js middleware for ImoOS tenant routing — extract tenant from subdomain, inject X-Tenant-Schema header, handle 403 mismatches. Auto-load when setting up Next.js or adding new routes.
argument-hint: [route] [tenant-strategy]
allowed-tools: Read, Write
---

# Next.js Tenant Routing — ImoOS

## Middleware (middleware.ts)
```typescript
// middleware.ts (root level)
import { NextRequest, NextResponse } from 'next/server';
import { jwtDecode } from 'jwt-decode';

export function middleware(request: NextRequest) {
  const host = request.headers.get('host') || '';
  const subdomain = host.split('.')[0]; // empresa-a.imos.cv → empresa-a

  // Skip for public routes
  if (request.nextUrl.pathname.startsWith('/auth') ||
      request.nextUrl.pathname.startsWith('/api/auth')) {
    return NextResponse.next();
  }

  // Get token from cookie
  const token = request.cookies.get('access_token')?.value;
  if (!token) {
    return NextResponse.redirect(new URL('/auth/login', request.url));
  }

  try {
    const claims = jwtDecode<{ tenant_schema: string }>(token);
    const expectedSchema = subdomain.replace(/-/g, '_'); // empresa-a → empresa_a

    if (claims.tenant_schema !== expectedSchema) {
      // Token is for a different tenant — redirect to correct subdomain
      return NextResponse.redirect(
        new URL(request.nextUrl.pathname,
          `https://${claims.tenant_schema.replace(/_/g, '-')}.imos.cv`)
      );
    }

    // Inject tenant header for API requests via Next.js server components
    const response = NextResponse.next();
    response.headers.set('X-Tenant-Schema', claims.tenant_schema);
    return response;
  } catch {
    return NextResponse.redirect(new URL('/auth/login', request.url));
  }
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

## Key Rules
- Tenant is determined from subdomain — NEVER from query params or body
- JWT claim `tenant_schema` is the source of truth for authorization
- Mismatch between subdomain and JWT claim → redirect (not 403) for UX
- Server components inject `X-Tenant-Schema` header to Django API
