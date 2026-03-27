# Sprint 5 — Dashboard Analytics

## Pré-requisitos — Ler antes de começar

```
frontend/src/app/page.tsx           → dashboard existe, ler estado actual
frontend/src/hooks/useTenantStats.ts → hook existe, ver o que já busca
apps/projects/views.py              → verificar se há endpoint de stats
apps/inventory/views.py             → verificar se há endpoint de stats
apps/crm/views.py                   → pipeline action já existe
apps/contracts/views.py             → contratos por status
```

```bash
grep -r "stats\|analytics\|summary" apps/ --include="*.py" -l
```

## Skills a carregar

```
@.claude/skills/06-module-projects/project-stats/SKILL.md
@.claude/skills/02-backend-django/drf-viewset-builder/SKILL.md
@.claude/skills/04-frontend-nextjs/react-query-patterns/SKILL.md
@.claude/skills/05-module-tenants/tenant-stats/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `drf-viewset-builder` | Endpoint `/api/v1/dashboard/stats/` |
| `react-component-builder` | Componentes de métricas no dashboard |

---

## Tarefa 1 — Backend: endpoint de stats do dashboard

**Verificar** se já existe algum endpoint de stats:
```bash
grep -r "DashboardStats\|dashboard.*stats\|summary" apps/ --include="*.py" -l
```

Criar `apps/core/views.py` (ou adicionar se já existe) — endpoint de stats agregadas:

```python
# GET /api/v1/dashboard/stats/
# Retorna métricas agregadas do tenant em contexto

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get(self, request):
        from apps.inventory.models import Unit
        from apps.crm.models import Lead, UnitReservation
        from apps.contracts.models import Contract, Payment

        # Inventário
        unit_qs = Unit.objects.all()
        inventory = {
            'total': unit_qs.count(),
            'available': unit_qs.filter(status=Unit.STATUS_AVAILABLE).count(),
            'reserved': unit_qs.filter(status=Unit.STATUS_RESERVED).count(),
            'contract': unit_qs.filter(status=Unit.STATUS_CONTRACT).count(),
            'sold': unit_qs.filter(status=Unit.STATUS_SOLD).count(),
        }

        # Receita — soma dos contratos ACTIVE + COMPLETED
        from django.db.models import Sum
        revenue_cve = (
            Contract.objects
            .filter(status__in=[Contract.STATUS_ACTIVE, Contract.STATUS_COMPLETED])
            .aggregate(total=Sum('total_price_cve'))['total'] or 0
        )

        # CRM pipeline counts
        from django.db.models import Count
        pipeline = (
            Lead.objects
            .values('stage')
            .annotate(count=Count('id'))
            .order_by('stage')
        )

        # Reservas activas a expirar nas próximas 24h
        from django.utils import timezone
        from datetime import timedelta
        expiring_soon = UnitReservation.objects.filter(
            status=UnitReservation.STATUS_ACTIVE,
            expires_at__lte=timezone.now() + timedelta(hours=24),
        ).count()

        # Contratos por status
        contracts = (
            Contract.objects
            .values('status')
            .annotate(count=Count('id'))
        )

        return Response({
            'inventory': inventory,
            'revenue_cve': str(revenue_cve),
            'pipeline': {item['stage']: item['count'] for item in pipeline},
            'reservations_expiring_soon': expiring_soon,
            'contracts': {item['status']: item['count'] for item in contracts},
        })
```

**Registar** em `config/urls.py`:
```python
path('api/v1/dashboard/', include('apps.core.dashboard_urls')),
```

---

## Tarefa 2 — Frontend: hook `useDashboardStats`

**Ler `frontend/src/hooks/useTenantStats.ts` antes de editar** — pode já ter dados sobreponíveis.

Criar (ou actualizar) `frontend/src/hooks/useDashboardStats.ts`:

```typescript
export interface DashboardStats {
  inventory: {
    total: number;
    available: number;
    reserved: number;
    contract: number;
    sold: number;
  };
  revenue_cve: string;
  pipeline: Record<string, number>;
  reservations_expiring_soon: number;
  contracts: Record<string, number>;
}

export function useDashboardStats() {
  const { schema } = useTenant();
  return useQuery<DashboardStats>({
    queryKey: ['dashboard', 'stats', schema],
    queryFn: () => apiClient.get('/dashboard/stats/').then(r => r.data),
    staleTime: 60_000,      // 1 minuto — aceita dados ligeiramente stale
    refetchInterval: 300_000, // auto-refresh a cada 5 minutos
    enabled: !!schema,
  });
}
```

---

## Tarefa 3 — Frontend: componentes do dashboard

**Ler `frontend/src/app/page.tsx` completamente antes de editar.**

Actualizar `/` para mostrar:

### KPI Cards (linha topo)
- **Unidades Disponíveis** — `inventory.available` / `inventory.total` com barra de progresso
- **Receita Confirmada** — `revenue_cve` formatado em CVE
- **Leads Activos** — soma de stages não terminais (excl. WON/LOST)
- **Contratos Activos** — `contracts.ACTIVE`

```typescript
// Componente KpiCard — extrair para components/ui/KpiCard.tsx se não existir
interface KpiCardProps {
  label: string;
  value: string;
  sub?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon: React.ElementType;
  color: string; // Tailwind bg class
}
```

### Funil do pipeline CRM
Barras horizontais proporcionais por stage:
```
Novo           ████████████ 24
Contactado     ████████ 18
Visita Agend.  █████ 12
Proposta Env.  ████ 9
Negociação     ██ 5
Ganho          █ 3
```

### Tabela de projectos recentes
- Já existe `useProjects()` — manter a tabela de projectos recentes

### Alerta de reservas a expirar
```typescript
{stats.reservations_expiring_soon > 0 && (
  <div className="rounded-xl bg-amber-50 border border-amber-200 px-4 py-3 flex items-center gap-3">
    <AlertCircle className="h-5 w-5 text-amber-500 shrink-0" />
    <p className="text-sm font-bold text-amber-800">
      {stats.reservations_expiring_soon} reserva(s) a expirar nas próximas 24h
    </p>
    <Link href="/crm" className="ml-auto text-xs font-bold text-amber-700 hover:underline">
      Ver CRM →
    </Link>
  </div>
)}
```

---

## Verificação final

- [ ] `GET /api/v1/dashboard/stats/` retorna dados correctos
- [ ] Dashboard `/` mostra KPIs reais (não hardcoded)
- [ ] Funil de pipeline visível com contagens reais
- [ ] Alerta aparece quando `reservations_expiring_soon > 0`
- [ ] `npm run build` sem erros
- [ ] Query keys incluem `schema` para isolamento por tenant
