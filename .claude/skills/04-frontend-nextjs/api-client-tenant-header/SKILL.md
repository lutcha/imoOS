---
name: api-client-tenant-header
description: Axios/fetch client with automatic tenant header injection for ImoOS. Auto-load when setting up API calls from Next.js or React Native.
argument-hint: [client-type] [environment]
allowed-tools: Read, Write
---

# API Client with Tenant Header — ImoOS

## Axios Instance (Next.js)
```typescript
// lib/api-client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
});

// Request interceptor: inject JWT and tenant header
apiClient.interceptors.request.use((config) => {
  const token = getAccessToken(); // From httpOnly cookie via /api/auth route
  const tenantSchema = getTenantSchema(); // From JWT decode

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (tenantSchema) {
    config.headers['X-Tenant-Schema'] = tenantSchema;
  }
  return config;
});

// Response interceptor: handle token expiry
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        return apiClient.request(error.config);
      }
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## React Query Integration
```typescript
// hooks/useUnits.ts
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import { useTenant } from '@/contexts/TenantContext';

export function useUnits(filters: UnitFilters) {
  const { schema } = useTenant();

  return useQuery({
    queryKey: ['units', schema, filters],  // tenant in cache key!
    queryFn: () => apiClient.get('/api/v1/units/', { params: filters }),
    staleTime: 30_000,
  });
}
```

## Key Rules
- Cache keys MUST include tenant schema — prevents cross-tenant cache contamination
- Never store JWT in localStorage — use httpOnly cookies (XSS protection)
- On 401, attempt token refresh once; if fails, redirect to login
- `X-Tenant-Schema` header is for observability/logging; Django uses the JWT claim for actual auth
