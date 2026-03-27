# Sprint 8 — Mobile: Preparação para Release (iOS + Android)

## Contexto

A app mobile (React Native + WatermelonDB) foi implementada nos Sprints 5-6.
Este prompt prepara a app para:
1. **TestFlight** (iOS) e **Internal Testing** (Android)
2. Corrigir problemas de UX identificados em testes internos
3. App icon, splash screen, sobre página
4. Deep links para /sign/{token} (e-signature)

## Pré-requisitos — Ler antes de começar

```
mobile/package.json             → versão actual + dependências
mobile/app.json                 → Expo config (name, bundleId, etc.)
mobile/src/auth/                → SecureStore, apiClient
mobile/src/screens/             → ecrãs existentes
mobile/src/data/sync.ts         → pullSync / bidirectionalSync
```

```bash
cat mobile/app.json
ls mobile/src/screens/
cat mobile/src/auth/apiClient.ts | head -30
```

## Skills a carregar

```
@.claude/skills/10-mobile/expo-config/SKILL.md
@.claude/skills/10-mobile/offline-first-patterns/SKILL.md
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `react-component-builder` | Splash screen, App icon, About page |
| `nextjs-tenant-routing` | Deep links para e-signature |

---

## Tarefa 1 — app.json: configuração de release

**Ler `mobile/app.json` antes de editar.**

```json
{
  "expo": {
    "name": "ImoOS",
    "slug": "imoos",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#1E40AF"
    },
    "ios": {
      "supportsTablet": false,
      "bundleIdentifier": "cv.imos.app",
      "buildNumber": "1",
      "config": {
        "usesNonExemptEncryption": false
      }
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#1E40AF"
      },
      "package": "cv.imos.app",
      "versionCode": 1,
      "permissions": [
        "CAMERA",
        "READ_EXTERNAL_STORAGE",
        "WRITE_EXTERNAL_STORAGE",
        "ACCESS_NETWORK_STATE",
        "RECEIVE_BOOT_COMPLETED"
      ]
    },
    "plugins": [
      "expo-secure-store",
      "expo-camera",
      [
        "expo-build-properties",
        {
          "android": { "compileSdkVersion": 34, "targetSdkVersion": 34, "buildToolsVersion": "34.0.0" },
          "ios": { "deploymentTarget": "15.0" }
        }
      ]
    ],
    "scheme": "imoos",
    "extra": {
      "eas": { "projectId": "FILL_IN_EAS_PROJECT_ID" }
    }
  }
}
```

---

## Tarefa 2 — Deep links para e-signature

O fluxo de assinatura electrónica (Sprint 6) envia um link `https://imos.cv/sign/{token}`.
Quando o comprador abre este link no telemóvel, deve abrir a app mobile (se instalada)
ou o browser (fallback).

Configurar deep links em `app.json`:
```json
"scheme": "imoos",
"intentFilters": [
  {
    "action": "VIEW",
    "data": [{ "scheme": "https", "host": "*.imos.cv", "pathPrefix": "/sign/" }],
    "category": ["BROWSABLE", "DEFAULT"]
  }
]
```

Criar `mobile/src/screens/SignatureScreen.tsx`:
```typescript
// Recebe token via deep link: imoos://sign/UUID ou https://imos.cv/sign/UUID
// 1. GET /sign/{token}/ (API pública — sem auth) → dados do contrato
// 2. Canvas de assinatura (react-native-signature-canvas)
// 3. POST /sign/{token}/ com PNG base64
// 4. Mostrar confirmação: "Contrato assinado. Receberá o PDF via WhatsApp."
```

---

## Tarefa 3 — Ecrã "Sobre" e configurações

Criar `mobile/src/screens/SettingsScreen.tsx`:
```typescript
// Secções:
// - Perfil: nome, email, role, empresa
// - Sincronização: última sincronização, botão "Sincronizar agora"
// - Notificações: toggle para push notifications
// - Sobre: versão da app, termos de uso, política de privacidade
// - Sair: logout (limpar SecureStore + navegar para LoginScreen)
```

---

## Tarefa 4 — eas.json para builds

Criar `mobile/eas.json`:
```json
{
  "cli": { "version": ">= 5.9.1" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "android": { "gradleCommand": ":app:assembleDebug" },
      "ios": { "buildConfiguration": "Debug" }
    },
    "preview": {
      "distribution": "internal",
      "android": { "buildType": "apk" }
    },
    "production": {
      "android": { "buildType": "app-bundle" }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "FILL_IN",
        "ascAppId": "FILL_IN",
        "appleTeamId": "FILL_IN"
      },
      "android": {
        "serviceAccountKeyPath": "./google-services.json",
        "track": "internal"
      }
    }
  }
}
```

---

## Tarefa 5 — Comandos de build

```bash
# Build preview para testar internamente
cd mobile
npx eas build --platform android --profile preview
npx eas build --platform ios --profile development

# Submeter para TestFlight
npx eas submit --platform ios --latest

# Submit para Android Internal Testing
npx eas submit --platform android --latest
```

---

## Verificação final

- [ ] `npx expo start` → app arranca sem erros
- [ ] Login com `admin@demo.cv` / `ImoOS2026!` funciona na app
- [ ] Pull sync carrega projectos e unidades offline
- [ ] Deep link `imoos://sign/UUID` abre SignatureScreen
- [ ] Build Android APK gerado com `eas build --profile preview`
- [ ] App icon e splash screen com branding ImoOS (azul #1E40AF)
- [ ] Ecrã "Sobre" mostra versão 1.0.0
