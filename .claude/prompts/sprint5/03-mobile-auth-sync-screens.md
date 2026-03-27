# Sprint 5 — Mobile: Auth + Sync + Ecrãs

## Estado actual (confirmado)

```
mobile/src/data/schema.ts          ✅ — projects, units, leads (3 tabelas)
mobile/src/data/models/            ✅ — Project.ts, Unit.ts, Lead.ts
mobile/src/data/database.ts        ✅ — database inicializado
mobile/src/auth/                   ❌ — não existe
mobile/src/screens/                ❌ — não existe (só directório vazio)
mobile/src/components/             ❌ — não existe (só directório vazio)
```

**Verificar** antes de começar:
```bash
ls mobile/src/
cat mobile/src/data/database.ts
cat mobile/package.json | grep '"name"\|"dependencies"' -A 30
```

## Skills a carregar

```
@.claude/skills/10-mobile/react-native-auth/SKILL.md
@.claude/skills/10-mobile/watermelondb-sync/SKILL.md
@.claude/skills/10-mobile/offline-first-patterns/SKILL.md
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
```

---

## Tarefa 1 — Auth: SecureStore + apiClient

**Verificar** se já existe qualquer ficheiro em `mobile/src/auth/`.

Criar `mobile/src/auth/tokenStore.ts`:
```typescript
// SecureStore = Keychain (iOS) / EncryptedSharedPreferences (Android)
// NUNCA usar AsyncStorage para tokens — não é seguro
import * as SecureStore from 'expo-secure-store';

const REFRESH_KEY = 'imos_refresh_token';
const SCHEMA_KEY  = 'imos_tenant_schema';

export const tokenStore = {
  async saveSession(refreshToken: string, tenantSchema: string) {
    await SecureStore.setItemAsync(REFRESH_KEY, refreshToken);
    await SecureStore.setItemAsync(SCHEMA_KEY, tenantSchema);
  },
  async getRefresh(): Promise<string | null> {
    return SecureStore.getItemAsync(REFRESH_KEY);
  },
  async getTenantSchema(): Promise<string | null> {
    return SecureStore.getItemAsync(SCHEMA_KEY);
  },
  async clear() {
    await SecureStore.deleteItemAsync(REFRESH_KEY);
    await SecureStore.deleteItemAsync(SCHEMA_KEY);
  },
};
```

Criar `mobile/src/auth/apiClient.ts`:
```typescript
import axios from 'axios';
import { tokenStore } from './tokenStore';

export const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

let accessToken: string | null = null;
export const setAccessToken = (t: string | null) => { accessToken = t; };

export const apiClient = axios.create({ baseURL: `${BASE_URL}/api/v1/` });

// Injectar Bearer token
apiClient.interceptors.request.use((cfg) => {
  if (accessToken) cfg.headers.Authorization = `Bearer ${accessToken}`;
  return cfg;
});

// Refresh automático em 401
apiClient.interceptors.response.use(
  (r) => r,
  async (error) => {
    if (error.response?.status !== 401) return Promise.reject(error);
    const refresh = await tokenStore.getRefresh();
    if (!refresh) return Promise.reject(error);
    try {
      const { data } = await axios.post(
        `${BASE_URL}/api/v1/users/auth/token/refresh/`,
        { refresh },
      );
      setAccessToken(data.access);
      error.config.headers.Authorization = `Bearer ${data.access}`;
      return axios.request(error.config);
    } catch {
      setAccessToken(null);
      await tokenStore.clear();
      return Promise.reject(error);
    }
  }
);
```

---

## Tarefa 2 — AuthContext mobile

Criar `mobile/src/auth/AuthContext.tsx`:
```typescript
import React, { createContext, useContext, useEffect, useState } from 'react';
import axios from 'axios';
import { tokenStore, BASE_URL } from './tokenStore';  // ajustar imports
import { setAccessToken } from './apiClient';

interface AuthState {
  isLoading: boolean;
  isAuthenticated: boolean;
  tenantSchema: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [tenantSchema, setTenantSchema] = useState<string | null>(null);

  // Restaurar sessão no arranque
  useEffect(() => {
    (async () => {
      const refresh = await tokenStore.getRefresh();
      if (refresh) {
        try {
          const { data } = await axios.post(
            `${BASE_URL}/api/v1/users/auth/token/refresh/`,
            { refresh },
          );
          setAccessToken(data.access);
          const schema = await tokenStore.getTenantSchema();
          setTenantSchema(schema);
          setIsAuthenticated(true);
        } catch {
          await tokenStore.clear();
        }
      }
      setIsLoading(false);
    })();
  }, []);

  const login = async (email: string, password: string) => {
    const { data } = await axios.post(`${BASE_URL}/api/v1/users/auth/token/`, {
      email, password,
    });
    setAccessToken(data.access);
    // Extrair tenant_schema do payload JWT
    const payload = JSON.parse(
      Buffer.from(data.access.split('.')[1], 'base64').toString()
    );
    await tokenStore.saveSession(data.refresh, payload.tenant_schema ?? '');
    setTenantSchema(payload.tenant_schema ?? null);
    setIsAuthenticated(true);
  };

  const logout = async () => {
    setAccessToken(null);
    await tokenStore.clear();
    setIsAuthenticated(false);
    setTenantSchema(null);
  };

  return (
    <AuthContext.Provider value={{ isLoading, isAuthenticated, tenantSchema, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
};
```

---

## Tarefa 3 — Sync pull-only (delta)

Criar `mobile/src/data/sync.ts`:
```typescript
import { synchronize } from '@nozbe/watermelondb/sync';
import { database } from './database';
import { apiClient } from '../auth/apiClient';

export async function pullSync() {
  await synchronize({
    database,
    pullChanges: async ({ lastPulledAt }) => {
      const params: Record<string, string> = {};
      if (lastPulledAt) {
        params.updated_after = new Date(lastPulledAt).toISOString();
      }

      const [projectsRes, unitsRes, leadsRes] = await Promise.all([
        apiClient.get('/projects/projects/', { params: { ...params, page_size: 200 } }),
        apiClient.get('/inventory/units/',   { params: { ...params, page_size: 500 } }),
        apiClient.get('/crm/leads/',         { params: { ...params, page_size: 200 } }),
      ]);

      return {
        changes: {
          projects: {
            created: projectsRes.data.results.map((p: any) => ({
              id: p.id,
              remote_id: p.id,
              name: p.name ?? '',
              slug: p.slug ?? '',
              status: p.status ?? '',
              city: p.city ?? '',
              address: p.address ?? '',
              created_at: new Date(p.created_at).getTime(),
              updated_at: new Date(p.updated_at).getTime(),
            })),
            updated: [],
            deleted: [],
          },
          units: {
            created: unitsRes.data.results.map((u: any) => ({
              id: u.id,
              remote_id: u.id,
              project_id: u.floor_project_id ?? '',
              number: u.code ?? '',
              status: u.status ?? '',
              unit_type: u.unit_type_detail?.name ?? '',
              price: parseFloat(u.pricing?.final_price_cve ?? '0'),
              created_at: new Date(u.created_at).getTime(),
              updated_at: new Date(u.updated_at).getTime(),
            })),
            updated: [],
            deleted: [],
          },
          leads: {
            created: leadsRes.data.results.map((l: any) => ({
              id: l.id,
              remote_id: l.id,
              first_name: l.first_name ?? '',
              last_name: l.last_name ?? '',
              email: l.email ?? '',
              phone: l.phone ?? '',
              status: l.status ?? '',
              budget: parseFloat(l.budget ?? '0'),
              created_at: new Date(l.created_at).getTime(),
              updated_at: new Date(l.updated_at).getTime(),
            })),
            updated: [],
            deleted: [],
          },
        },
        timestamp: Date.now(),
      };
    },
    pushChanges: async () => {
      // Pull-only neste sprint — push sync em Sprint 6 (relatórios de obra)
    },
  });
}
```

---

## Tarefa 4 — Ecrãs

### `mobile/src/screens/LoginScreen.tsx`
```typescript
// Form simples: email + password + botão
// useAuth().login() → navega para (tabs) ao sucesso
// Erro 401 → "Credenciais incorrectas"
// Erro de rede → "Sem ligação — verifique a sua ligação à internet"
```

### `mobile/src/screens/ProjectsScreen.tsx`
```typescript
// withObservables: lista de projects do WatermelonDB
// Pull-to-refresh → chama pullSync()
// Indicador "Última sincronização: {syncedAt}"
// Funciona completamente OFFLINE com dados em cache
```

### `mobile/src/screens/ProjectDetailScreen.tsx`
```typescript
// Recebe projectId como param de navegação
// Lista unidades relacionadas (units.project_id == projectId)
// Status badges com cores
```

---

## Tarefa 5 — Navegação (`mobile/App.tsx`)

```typescript
// Stack navigator:
//   - AuthStack: LoginScreen (se !isAuthenticated)
//   - AppTabs: ProjectsScreen | LeadsScreen | ProfileScreen (se isAuthenticated)
// Loading splash enquanto isLoading=true (restaurar sessão)
```

---

## Verificação final

- [ ] App corre em Expo Go (`npx expo start`)
- [ ] Login com credenciais reais → armazena em SecureStore
- [ ] `pullSync()` preenche WatermelonDB com dados do backend
- [ ] `ProjectsScreen` funciona **sem internet** após primeiro sync
- [ ] Pull-to-refresh actualiza dados
- [ ] Logout limpa SecureStore
- [ ] Sem tokens em AsyncStorage (verificar com Expo DevTools → Storage)
