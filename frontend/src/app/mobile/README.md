# ImoOS Mobile — Interface para Equipas de Campo

Aplicação mobile-first para encarregados de obra gerirem tarefas de construção. Otimizada para:

- ✅ Telas pequenas (iPhone 8+)
- ✅ Conexões lentas (3G)
- ✅ Uso offline-first
- ✅ Visibilidade ao sol

## 📁 Estrutura

```
frontend/src/app/mobile/
├── layout.tsx              # Layout mobile (sem sidebar)
├── globals.css             # Estilos mobile-specific
├── page.tsx                # Redirect para /obra
├── register-sw.tsx         # Service Worker registration
├── obra/
│   ├── page.tsx            # Dashboard da obra com filtros, search, swipe
│   ├── layout.tsx          # Layout da secção obra
│   └── [taskId]/
│       └── page.tsx        # Detalhe da tarefa completo
├── sync/
│   └── page.tsx            # Página de gestão de sincronização
├── settings/
│   └── page.tsx            # Configurações e info da app
└── components/
    ├── MobileDesignSystem.tsx  # Tokens de design
    ├── MobileHeader.tsx        # Header otimizado
    ├── MobileBottomNav.tsx     # Navegação inferior
    ├── OfflineIndicator.tsx    # Banner online/offline
    ├── TaskCard.tsx            # Card com swipe actions
    ├── QuickStatusUpdate.tsx   # 🔴🟡🟢 selector
    ├── PhotoUpload.tsx         # Camera + compressão
    ├── VoiceRecorder.tsx       # Notas de voz 30s
    └── SyncBadge.tsx           # Status de sync

frontend/src/lib/mobile/
├── image-compression.ts    # Compressão <500KB
├── api-sync.ts             # API client para sync
└── mobile-db.ts            # IndexedDB wrapper (existente)

frontend/src/hooks/
├── useMobileTasks.ts       # Tasks com IndexedDB
├── useOfflineSync.ts       # Sync completo com retry
└── mobile/
    └── useConstructionTasksMobile.ts  # TanStack Query

frontend/public/
├── manifest.json           # PWA manifest
├── sw.js                   # Service Worker
└── icons/                  # Ícones PWA

frontend/src/test/mobile/   # Testes unitários
```

## 🚀 Quick Start

### 1. Instalar dependências

```bash
cd frontend
npm install
```

### 2. Configurar PWA

O `manifest.json` está configurado em `public/manifest.json`. O Service Worker em `public/sw.js`.

Adicionar ao layout raiz se ainda não existir:

```tsx
// app/layout.tsx
import { RegisterSW } from "./register-sw";

export const metadata = {
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "ImoOS Obra",
  },
};

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <RegisterSW />
        {children}
      </body>
    </html>
  );
}
```

### 3. Configurar Next.js

```typescript
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  headers: async () => [
    {
      source: "/sw.js",
      headers: [
        {
          key: "Cache-Control",
          value: "public, max-age=0, must-revalidate",
        },
        {
          key: "Service-Worker-Allowed",
          value: "/",
        },
      ],
    },
  ],
};

export default nextConfig;
```

## 🎨 Design System

### Touch Targets

- Mínimo: **48px** (WCAG 2.1)
- Botões principais: **56-64px**
- Cards: padding **16-20px**

### Cores de Status

| Status | Cor | Icon |
|--------|-----|------|
| Não Iniciado | 🔴 Red-500 | 🔴 |
| Em Andamento | 🟡 Amber-500 | 🟡 |
| Concluído | 🟢 Green-500 | 🟢 |
| Bloqueado | ⚫ Gray-500 | ⚫ |

### Funcionalidades da Lista (/mobile/obra)

- **Pull-to-refresh**: Puxe para baixo para atualizar
- **Filtros rápidos**: Todas, Hoje, Atrasadas, Urgentes, Em Andamento
- **Ordenação**: Por data, prioridade, nome, status
- **Search**: Pesquisa por nome, projeto, descrição
- **Swipe actions**: Direita = Concluir, Esquerda = Reportar Problema

### Funcionalidades do Detalhe (/mobile/obra/[taskId])

- **Status update**: Seletor 🔴🟡🟢 grande
- **Ações rápidas**: Botões grandes para status
- **Fotos**: Grid 3 colunas, compressão automática
- **Notas de voz**: Gravação até 30s, preview antes de enviar
- **Notas de texto**: Textarea para observações
- **Histórico**: Timeline de alterações

## 📡 Offline-First

### Fluxo de Sync

1. **Update Local**: Guarda em IndexedDB imediatamente
2. **Queue Action**: Adiciona à fila de sync
3. **Try Network**: Se online, tenta enviar
4. **Background Sync**: Service Worker processa quando online
5. **Retry**: Exponential backoff (5s, 15s, 30s, 60s, 5min)
6. **Conflict Resolution**: Last write wins

### IndexedDB Schema

```
imos_mobile_db (v1)
├── tasks (keyPath: id, indexes: status, dueDate, projectId)
├── photos (keyPath: id, indexes: taskId, synced)
├── voiceNotes (keyPath: id, indexes: taskId, synced)
├── actions (autoIncrement, indexes: timestamp, type)
└── syncMeta (keyPath: key)
```

### API de Sync

```typescript
import { useOfflineSync } from "@/hooks/useOfflineSync";

function MyComponent() {
  const { 
    isOnline, 
    pendingCount, 
    isSyncing, 
    syncNow,
    queueAction 
  } = useOfflineSync();
  
  const handleComplete = async (taskId: string) => {
    // 1. Update local
    await updateTaskLocal(taskId, 'completed');
    
    // 2. Queue for sync
    await queueAction({
      type: 'task_complete',
      payload: { taskId },
    });
  };
}
```

## 🧪 Testes

### Executar testes

```bash
# Testes unitários
npm test

# Com cobertura
npm run test:coverage

# Testes E2E
npm run test:e2e
```

### Testar Offline

1. Abrir app em modo normal
2. Ativar "Airplane Mode"
3. Fazer alterações
4. Verificar badge "Pendente sincronizar"
5. Desativar Airplane Mode
6. Verificar sync automático

### Testar PWA

1. Abrir Chrome DevTools
2. Lighthouse → PWA
3. Verificar critérios
4. Testar "Add to Home Screen"

## 📱 iOS PWA

Para instalar no iOS:

1. Abrir Safari
2. Navegar para `/mobile/obra`
3. Tap "Share" → "Add to Home Screen"
4. App abre em standalone mode

### Ícones necessários

Criar em `public/icons/`:
- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

## 🌐 APIs Utilizadas

```
GET    /api/v1/construction/tasks/              # Listar tarefas
GET    /api/v1/construction/tasks/{id}/         # Detalhe
PATCH  /api/v1/construction/tasks/{id}/         # Atualizar status
POST   /api/v1/construction/tasks/{id}/photos/  # Upload foto
POST   /api/v1/construction/tasks/{id}/voice-notes/ # Upload voz
POST   /api/v1/construction/tasks/{id}/notes/   # Adicionar nota
```

## 📊 Performance Targets

| Métrica | Target |
|---------|--------|
| Bundle inicial | < 500KB |
| First Contentful Paint | < 1.5s (3G) |
| Time to Interactive | < 3s |
| Tamanho de foto | < 500KB |
| Cache de tasks | 5 min stale |
| Sync retry | Exponential backoff |

## 🐛 Troubleshooting

### Problema: Fotos não comprimem
**Solução**: Verificar se `canvas` é suportado. Fallback para upload direto.

### Problema: Sync não funciona offline
**Solução**: Verificar `navigator.onLine` e event listeners.

### Problema: IndexedDB falha
**Solução**: Verificar quota de storage em Safari Settings → Advanced.

### Problema: Service Worker não regista
**Solução**: Verificar HTTPS (obrigatório para SW exceto localhost).

### Problema: Swipe não funciona
**Solução**: Verificar touch events não estão bloqueados por parent elements.

## 📄 Licença

Parte do ImoOS — Sistema de Gestão Imobiliária para Cabo Verde.
