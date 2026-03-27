---
name: offline-first-pattern
description: Offline-capable UI patterns for ImoOS — service worker caching, mutation queue, online/offline indicator. Auto-load when building features that need offline support.
argument-hint: [feature] [sync-strategy]
allowed-tools: Read, Write
---

# Offline-First Pattern — ImoOS (Web)

## Online/Offline Detection
```typescript
// hooks/useOnlineStatus.ts
import { useState, useEffect } from 'react';

export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}
```

## Offline Indicator Component
```typescript
// components/OfflineIndicator.tsx
export function OfflineIndicator() {
  const isOnline = useOnlineStatus();
  if (isOnline) return null;
  return (
    <div className="fixed top-0 left-0 right-0 bg-amber-500 text-white text-center py-1 text-sm z-50">
      Sem ligação — a trabalhar em modo offline. As alterações serão sincronizadas quando a rede voltar.
    </div>
  );
}
```

## Mutation Queue (IndexedDB via React Query)
```typescript
// For the web app, use React Query's offline capabilities
import { QueryClient } from '@tanstack/react-query';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';
import { persistQueryClient } from '@tanstack/react-query-persist-client';

const persister = createSyncStoragePersister({ storage: window.localStorage });
persistQueryClient({ queryClient, persister, maxAge: 24 * 60 * 60 * 1000 });

// Mutations are queued and retried automatically when online
const mutation = useMutation({
  mutationFn: createDailyLog,
  networkMode: 'offlineFirst',  // Queue when offline, execute when online
});
```

## Key Rules
- Mobile App uses WatermelonDB (SQLite) for true offline-first — see daily-log-offline-sync skill
- Web app uses service worker + React Query persistence for lighter offline support
- Always show offline indicator — users in construction sites may not notice connectivity loss
- Sync errors must be visible to user — never silently fail a queued mutation
