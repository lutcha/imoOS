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
├── obra/
│   ├── page.tsx            # Dashboard da obra
│   └── [taskId]/
│       └── page.tsx        # Detalhe da tarefa
└── components/
    ├── MobileDesignSystem.tsx  # Tokens de design
    ├── MobileHeader.tsx        # Header otimizado
    ├── MobileBottomNav.tsx     # Navegação inferior
    ├── OfflineIndicator.tsx    # Banner online/offline
    ├── TaskCard.tsx            # Card com swipe
    ├── QuickStatusUpdate.tsx   # 🔴🟡🟢 selector
    ├── PhotoUpload.tsx         # Camera + compressão
    ├── VoiceRecorder.tsx       # Notas de voz
    └── SyncBadge.tsx           # Status de sync

frontend/src/lib/mobile/
├── image-compression.ts    # Compressão <500KB
└── sync-manager.ts         # Background sync

frontend/src/hooks/
├── useMobileTasks.ts       # (existente) Tasks com IndexedDB
├── useOfflineSync.ts       # (existente) Sync queue
└── useConstructionTasksMobile.ts  # TanStack Query otimizado
```

## 🚀 Quick Start

### 1. Instalar dependências

```bash
cd frontend
npm install
```

### 2. Configurar PWA

O `manifest.json` já está configurado em `public/manifest.json`. Adicionar ao layout raiz:

```tsx
// app/layout.tsx
export const metadata = {
  // ... existing metadata
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "ImoOS Obra",
  },
};
```

### 3. Registar Service Worker

Criar `app/register-sw.tsx`:

```tsx
"use client";

import { useEffect } from "react";

export function RegisterSW() {
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker
        .register("/sw.js")
        .then((reg) => console.log("SW registered:", reg))
        .catch((err) => console.log("SW registration failed:", err));
    }
  }, []);

  return null;
}
```

E adicionar ao layout:

```tsx
import { RegisterSW } from "./register-sw";

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

### Tipografia

- Base: **16px** (acessibilidade)
- Títulos: **18-20px bold**
- Labels: **12px uppercase semibold**

## 📡 Offline-First

### Fluxo de Sync

1. **Update Local**: Guarda em IndexedDB imediatamente
2. **Queue Action**: Adiciona à fila de sync
3. **Try Network**: Se online, tenta enviar
4. **Background Sync**: Quando online, processa fila
5. **Retry**: Exponential backoff (5s, 15s, 30s, 60s)

### IndexedDB Schema

```
imos_mobile_db (v1)
├── tasks (keyPath: id)
├── photos (keyPath: id, indexes: taskId, synced)
├── voiceNotes (keyPath: id, indexes: taskId, synced)
├── actions (autoIncrement, indexes: timestamp, type)
└── syncMeta (keyPath: key)
```

## 🧪 Testes

### Testar Offline

1. Abrir app em modo normal
2. Ativar "Airplane Mode"
3. Fazer alterações
4. Verificar badge "Pendente sincronizar"
5. Desativar Airplane Mode
6. Verificar sync automático

### Testar Compressão de Fotos

```tsx
import { compressPhoto } from "@/lib/mobile/image-compression";

const compressed = await compressPhoto(file, {
  maxWidth: 1200,
  quality: 0.7,
  maxSizeMB: 0.5,
});

console.log(`Original: ${file.size / 1024}KB`);
console.log(`Compressed: ${compressed.size / 1024}KB`);
```

## 🔧 Configuração Next.js

### next.config.ts

```typescript
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
GET    /api/v1/construction/tasks/         # Listar tarefas
GET    /api/v1/construction/tasks/{id}/    # Detalhe
PATCH  /api/v1/construction/tasks/{id}/    # Atualizar status
POST   /api/v1/construction/tasks/{id}/photos/      # Upload foto
POST   /api/v1/construction/tasks/{id}/voice-notes/ # Upload voz
```

## 📊 Performance Targets

| Métrica | Target |
|---------|--------|
| Bundle inicial | < 500KB |
| First Contentful Paint | < 1.5s (3G) |
| Time to Interactive | < 3s |
| Tamanho de foto | < 500KB |
| Cache de tasks | 5 min stale |

## 🐛 Troubleshooting

### Problema: Fotos não comprimem
**Solução**: Verificar se `canvas` é suportado. Fallback para upload direto.

### Problema: Sync não funciona offline
**Solução**: Verificar `navigator.onLine` e event listeners.

### Problema: IndexedDB falha
**Solução**: Verificar quota de storage em Safari Settings → Advanced.

## 📄 Licença

Parte do ImoOS — Sistema de Gestão Imobiliária para Cabo Verde.
