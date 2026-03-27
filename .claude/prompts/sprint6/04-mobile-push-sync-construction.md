# Sprint 6 — Mobile: Push Sync + Relatórios de Obra

## Contexto

No Sprint 5, a app mobile implementou **pull-only sync** (delta via `updated_after`).
Este sprint adiciona:
1. **Push sync**: submeter relatórios de obra criados offline para o backend
2. **Ecrã de relatórios de obra** (`DailyReport`) com suporte offline-first
3. **Push notifications** (Expo Notifications) para alertas de sincronização

O módulo `apps/construction/` já existe e está completo (Sprint 5).
O WatermelonDB já tem as tabelas `projects`, `units`, `leads` no schema.

## Pré-requisitos — Ler antes de começar

```
mobile/src/data/schema.ts         → tabelas existentes
mobile/src/data/sync.ts           → pullSync() (pull-only, Sprint 5)
mobile/src/auth/apiClient.ts      → apiClient com Bearer + refresh
apps/construction/models.py       → DailyReport, ConstructionPhoto
apps/construction/views.py        → DailyReportViewSet (endpoints)
apps/construction/serializers.py  → DailyReportSerializer
```

```bash
cat mobile/src/data/schema.ts
cat mobile/src/data/sync.ts
grep "daily.report\|construction" apps/construction/urls.py
```

## Skills a carregar

```
@.claude/skills/10-mobile/watermelondb-sync/SKILL.md
@.claude/skills/10-mobile/offline-first-patterns/SKILL.md
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
@.claude/skills/11-module-construction/daily-report/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `nextjs-tenant-routing` | Endpoint backend para WatermelonDB push sync |
| `react-component-builder` | Ecrãs mobile: DailyReportList + DailyReportForm |
| `celery-task-specialist` | Task: process_construction_photo (já existe — verificar) |

---

## Tarefa 1 — WatermelonDB schema: tabela `daily_reports`

**Ler `mobile/src/data/schema.ts` antes de editar.**

Adicionar ao schema:
```typescript
tableSchema({
  name: 'daily_reports',
  columns: [
    { name: 'remote_id',     type: 'string' },
    { name: 'project_id',    type: 'string', isIndexed: true },
    { name: 'building_id',   type: 'string', isOptional: true },
    { name: 'date',          type: 'string' },          // ISO date YYYY-MM-DD
    { name: 'summary',       type: 'string' },
    { name: 'progress_pct',  type: 'number' },
    { name: 'status',        type: 'string' },          // DRAFT/SUBMITTED/APPROVED
    { name: 'weather',       type: 'string', isOptional: true },
    { name: 'workers_count', type: 'number' },
    { name: 'is_synced',     type: 'boolean' },         // false = criado offline
    { name: 'sync_error',    type: 'string', isOptional: true },
    { name: 'created_at',    type: 'number' },
    { name: 'updated_at',    type: 'number' },
  ],
}),
```

Criar `mobile/src/data/models/DailyReport.ts`:
```typescript
import { Model } from '@nozbe/watermelondb';
import { field, date, readonly } from '@nozbe/watermelondb/decorators';

export class DailyReport extends Model {
  static table = 'daily_reports';

  @field('remote_id')    remoteId!: string;
  @field('project_id')   projectId!: string;
  @field('building_id')  buildingId!: string;
  @field('date')         date!: string;
  @field('summary')      summary!: string;
  @field('progress_pct') progressPct!: number;
  @field('status')       status!: string;
  @field('weather')      weather!: string;
  @field('workers_count') workersCount!: number;
  @field('is_synced')    isSynced!: boolean;
  @field('sync_error')   syncError!: string;
  @readonly @date('created_at') createdAt!: Date;
  @readonly @date('updated_at') updatedAt!: Date;
}
```

---

## Tarefa 2 — Push sync (submeter relatórios offline)

**Ler `mobile/src/data/sync.ts` antes de editar.**

Actualizar `pullSync()` → `bidirectionalSync()`:
```typescript
import { synchronize } from '@nozbe/watermelondb/sync';

export async function bidirectionalSync() {
  await synchronize({
    database,
    pullChanges: async ({ lastPulledAt }) => {
      // ... mesmo código do Sprint 5, adicionar daily_reports:
      const reportsRes = await apiClient.get('/construction/daily-reports/', {
        params: { ...(lastPulledAt ? { updated_after: new Date(lastPulledAt).toISOString() } : {}), page_size: 200 },
      });

      return {
        changes: {
          // ... projects, units, leads (já existem)
          daily_reports: {
            created: reportsRes.data.results.map((r: any) => ({
              id: r.id,
              remote_id: r.id,
              project_id: r.project,
              building_id: r.building ?? '',
              date: r.date,
              summary: r.summary,
              progress_pct: r.progress_pct,
              status: r.status,
              weather: r.weather ?? '',
              workers_count: r.workers_count,
              is_synced: true,
              sync_error: '',
              created_at: new Date(r.created_at).getTime(),
              updated_at: new Date(r.updated_at).getTime(),
            })),
            updated: [],
            deleted: [],
          },
        },
        timestamp: Date.now(),
      };
    },

    pushChanges: async ({ changes }) => {
      const { daily_reports } = changes;
      if (!daily_reports) return;

      // Submeter novos relatórios criados offline
      for (const report of [...(daily_reports.created ?? []), ...(daily_reports.updated ?? [])]) {
        try {
          if (report.remote_id) {
            // Update
            await apiClient.patch(`/construction/daily-reports/${report.remote_id}/`, {
              summary: report.summary,
              progress_pct: report.progress_pct,
              weather: report.weather,
              workers_count: report.workers_count,
            });
          } else {
            // Create
            const { data } = await apiClient.post('/construction/daily-reports/', {
              project: report.project_id,
              building: report.building_id || null,
              date: report.date,
              summary: report.summary,
              progress_pct: report.progress_pct,
              weather: report.weather,
              workers_count: report.workers_count,
            });
            // Guardar remote_id
            await database.write(async () => {
              const localReport = await database.get<DailyReport>('daily_reports').find(report.id);
              await localReport.update(r => { r.remoteId = data.id; r.isSynced = true; });
            });
          }
        } catch (e: any) {
          // Marcar erro no registo local — não bloquear sync dos outros
          await database.write(async () => {
            const localReport = await database.get<DailyReport>('daily_reports').find(report.id);
            await localReport.update(r => { r.syncError = e?.message ?? 'Erro de sincronização'; });
          });
        }
      }
    },
  });
}
```

---

## Tarefa 3 — Ecrã: lista de relatórios

Criar `mobile/src/screens/DailyReportListScreen.tsx`:
```typescript
// withObservables: lista daily_reports ordenados por date desc
// Filtro por projecto (param de navegação)
// Badge de estado: DRAFT (cinza) | SUBMITTED (azul) | APPROVED (verde)
// Indicador de sync pendente: ícone ⚠ se !is_synced
// FAB: criar novo relatório → DailyReportFormScreen
// Pull-to-refresh → bidirectionalSync()
```

---

## Tarefa 4 — Ecrã: formulário de relatório (offline-first)

Criar `mobile/src/screens/DailyReportFormScreen.tsx`:
```typescript
// Campos: data (DatePicker), resumo (TextArea), progresso (Slider 0-100),
//         tempo (Select: Sol/Nublado/Chuva/Vento), nº trabalhadores (NumberInput)
// Submit: cria registo local com is_synced=false, sem chamar API
//   → feedback imediato ao utilizador: "Relatório guardado localmente"
// Se online: chama bidirectionalSync() automaticamente após guardar
// Se offline: mostra toast "Sem ligação — sincronizará quando disponível"

// Detectar conectividade:
import NetInfo from '@react-native-community/netinfo';
const { isConnected } = await NetInfo.fetch();
```

---

## Tarefa 5 — Push notifications (Expo)

Criar `mobile/src/notifications/setup.ts`:
```typescript
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) return null; // não funciona em simulador

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  if (finalStatus !== 'granted') return null;

  const token = (await Notifications.getExpoPushTokenAsync()).data;
  return token;
}

// Notificações a enviar:
// - "Sincronização concluída: X relatórios enviados"
// - "Erro de sincronização: Y relatórios falharam"
// - (futuro) "Novo comentário no seu relatório de obra"
```

---

## Verificação final

- [ ] Criar relatório offline (modo avião) → aparece na lista com ⚠
- [ ] Ligar à internet → `bidirectionalSync()` → relatório aparece no backend
- [ ] `GET /api/v1/construction/daily-reports/` → inclui relatório submetido
- [ ] `pullSync()` depois → `is_synced=true`, sem duplicados
- [ ] Erro de push (403 permissão) → marcado com `sync_error`, restantes sincronizam
- [ ] Pull-to-refresh na lista → actualiza dados
- [ ] Notificação push após sync bem-sucedido
