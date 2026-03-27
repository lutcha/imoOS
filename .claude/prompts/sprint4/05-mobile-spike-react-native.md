# Sprint 4 — Mobile Spike: React Native + WatermelonDB

## Contexto

Spike de arquitectura — **não é feature completa**.
Objectivo: provar que o padrão offline-first funciona para as condições de conectividade de Cabo Verde.
Resultado esperado: app funcional com auth + listagem de unidades + sync básico.

## Pré-requisitos — Ler antes de começar

```
mobile/              → verificar estado actual (pode já ter estrutura básica)
frontend/src/contexts/AuthContext.tsx  → padrão JWT a replicar
apps/inventory/views.py               → endpoints a consumir
```

```bash
ls mobile/
ls mobile/src/ 2>/dev/null || echo "NAO EXISTE"
```

## Skills a carregar

```
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md   # padrão JWT reutilizável
@.claude/skills/10-mobile/watermelondb-sync/SKILL.md
@.claude/skills/10-mobile/offline-first-patterns/SKILL.md
@.claude/skills/10-mobile/react-native-auth/SKILL.md
```

---

## Tarefa 1 — Verificar e inicializar estrutura mobile

**Se `mobile/` estiver vazio ou não existir**, inicializar:
```bash
cd mobile
npx create-expo-app . --template blank-typescript
```

**Se já tiver conteúdo** — ler `mobile/package.json` e `mobile/App.tsx` antes de qualquer edição.

Dependências a adicionar (verificar se já existem no package.json):
```bash
cd mobile && npx expo install \
  @nozbe/watermelondb \
  @react-native-async-storage/async-storage \
  expo-secure-store \
  axios \
  @tanstack/react-query \
  react-native-safe-area-context \
  react-native-screens
```

---

## Tarefa 2 — Auth mobile (JWT + SecureStore)

Criar `mobile/src/auth/`:

```typescript
// mobile/src/auth/tokenStore.ts
// Diferente do web: usar SecureStore (Keychain no iOS, EncryptedSharedPreferences no Android)
// NÃO usar AsyncStorage para tokens — não é seguro

import * as SecureStore from 'expo-secure-store';

const REFRESH_KEY = 'imos_refresh_token';

export const tokenStore = {
  async saveRefresh(token: string) {
    await SecureStore.setItemAsync(REFRESH_KEY, token);
  },
  async getRefresh(): Promise<string | null> {
    return SecureStore.getItemAsync(REFRESH_KEY);
  },
  async clearRefresh() {
    await SecureStore.deleteItemAsync(REFRESH_KEY);
  },
};
```

```typescript
// mobile/src/auth/apiClient.ts
// Mesmo padrão do frontend web mas adaptado para React Native
// Sem httpOnly cookies — usar SecureStore para refresh token
import axios from 'axios';
import { tokenStore } from './tokenStore';

export const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

let accessToken: string | null = null;

export const apiClient = axios.create({ baseURL: `${BASE_URL}/api/v1/` });

apiClient.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Refresh automático em 401
apiClient.interceptors.response.use(
  (r) => r,
  async (error) => {
    if (error.response?.status === 401) {
      const refresh = await tokenStore.getRefresh();
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE_URL}/api/v1/users/auth/token/refresh/`, { refresh });
          accessToken = data.access;
          error.config.headers.Authorization = `Bearer ${accessToken}`;
          return axios.request(error.config);
        } catch {
          accessToken = null;
          await tokenStore.clearRefresh();
          // Navegar para login — via evento ou navigation ref
        }
      }
    }
    return Promise.reject(error);
  }
);

export const setAccessToken = (token: string | null) => { accessToken = token; };
```

---

## Tarefa 3 — WatermelonDB: schema de unidades

```typescript
// mobile/src/database/schema.ts
import { appSchema, tableSchema } from '@nozbe/watermelondb';

export const schema = appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: 'units',
      columns: [
        { name: 'remote_id', type: 'string', isIndexed: true },
        { name: 'code', type: 'string' },
        { name: 'typology', type: 'string' },
        { name: 'area_sqm', type: 'number' },
        { name: 'status', type: 'string' },
        { name: 'price_cve', type: 'number' },
        { name: 'project_name', type: 'string' },
        { name: 'synced_at', type: 'number' },  // timestamp
      ],
    }),
  ],
});
```

```typescript
// mobile/src/database/models/Unit.ts
import { Model } from '@nozbe/watermelondb';
import { field, date } from '@nozbe/watermelondb/decorators';

export class Unit extends Model {
  static table = 'units';

  @field('remote_id') remoteId!: string;
  @field('code') code!: string;
  @field('typology') typology!: string;
  @field('area_sqm') areaSqm!: number;
  @field('status') status!: string;
  @field('price_cve') priceCve!: number;
  @field('project_name') projectName!: string;
  @date('synced_at') syncedAt!: Date;
}
```

---

## Tarefa 4 — Sync pull-only (MVP do spike)

```typescript
// mobile/src/database/sync.ts
// Pull-only para o spike — push sync fica para Sprint 5
import { synchronize } from '@nozbe/watermelondb/sync';
import { database } from './index';
import { apiClient } from '../auth/apiClient';

export async function syncUnits() {
  await synchronize({
    database,
    pullChanges: async ({ lastPulledAt }) => {
      const params = lastPulledAt ? `?updated_after=${new Date(lastPulledAt).toISOString()}` : '';
      const { data } = await apiClient.get(`/inventory/units/${params}`);

      return {
        changes: {
          units: {
            created: data.results.map((u: any) => ({
              id: u.id,
              remote_id: u.id,
              code: u.code,
              typology: u.unit_type?.typology ?? '',
              area_sqm: parseFloat(u.area_sqm ?? '0'),
              status: u.status,
              price_cve: parseFloat(u.pricing?.price_cve ?? '0'),
              project_name: u.floor?.building?.project?.name ?? '',
              synced_at: Date.now(),
            })),
            updated: [],
            deleted: [],
          },
        },
        timestamp: Date.now(),
      };
    },
    pushChanges: async () => {
      // Pull-only no spike — não há mudanças locais para enviar
    },
  });
}
```

---

## Tarefa 5 — Ecrã de unidades offline-first

```typescript
// mobile/src/screens/UnitsScreen.tsx
import { withObservables } from '@nozbe/watermelondb/react';
import { database } from '../database';
import { Unit } from '../database/models/Unit';

// Componente base
function UnitsScreenBase({ units }: { units: Unit[] }) {
  return (
    <FlatList
      data={units}
      keyExtractor={(u) => u.remoteId}
      renderItem={({ item }) => (
        <View>
          <Text>{item.code} — {item.typology}</Text>
          <Text>{item.priceCve.toLocaleString('pt-CV')} CVE</Text>
          <Text>{item.status}</Text>
        </View>
      )}
    />
  );
}

// Reactivo ao WatermelonDB — re-renderiza quando DB muda
const enhance = withObservables([], () => ({
  units: database.get<Unit>('units').query(),
}));

export const UnitsScreen = enhance(UnitsScreenBase);
```

---

## Verificação do Spike

- [ ] App corre em Expo Go / simulador iOS / emulador Android
- [ ] Login com credenciais do backend → token guardado em SecureStore
- [ ] `syncUnits()` preenche a base WatermelonDB
- [ ] Ecrã de unidades funciona **sem ligação à internet** (dados do WatermelonDB)
- [ ] Sync incrementa correctamente (só busca registos após `lastPulledAt`)
- [ ] Sem tokens em AsyncStorage (verificar com Expo DevTools)

## Notas de Arquitectura

- Pull-only no spike é intencional — push sync (para leads, visitas) fica para Sprint 5
- WatermelonDB usa SQLite nativo — funciona offline nativamente
- SecureStore é obrigatório para tokens — não negociável (LGPD Cabo Verde)
- `remote_id` armazenado separado do `id` local do WatermelonDB para o sync delta
