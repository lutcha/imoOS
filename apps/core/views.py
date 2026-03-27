from datetime import timedelta

from django.core.cache import cache
from django.db import connection
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsTenantMember


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def health_check(request):
    """
    Public health check endpoint for load balancers and deploy smoke tests.
    Returns 200 if DB and cache are reachable, 503 otherwise.
    """
    checks = {}

    # Database
    try:
        connection.ensure_connection()
        checks['db'] = 'ok'
    except Exception:
        checks['db'] = 'error'

    # Cache (Redis)
    try:
        cache.set('health_ping', '1', timeout=5)
        assert cache.get('health_ping') == '1'
        checks['cache'] = 'ok'
    except Exception:
        checks['cache'] = 'error'

    all_ok = all(v == 'ok' for v in checks.values())
    http_status = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    return Response({'status': 'ok' if all_ok else 'degraded', 'checks': checks}, status=http_status)


class DetailedHealthCheckView(APIView):
    """
    Detailed health check with DB, Redis, and migrations status.
    Requires super-admin authentication (IsAdminUser).
    Used for production monitoring and debugging.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        import time
        from django.db.migrations.executor import MigrationExecutor
        
        checks = {}

        # Database
        try:
            t0 = time.time()
            connection.ensure_connection()
            checks['database'] = {
                'status': 'ok',
                'latency_ms': round((time.time() - t0) * 1000, 1)
            }
        except Exception as e:
            checks['database'] = {'status': 'error', 'error': str(e)}

        # Redis
        try:
            t0 = time.time()
            cache.set('_health_check', '1', timeout=5)
            val = cache.get('_health_check')
            checks['redis'] = {
                'status': 'ok' if val == '1' else 'error',
                'latency_ms': round((time.time() - t0) * 1000, 1),
            }
        except Exception as e:
            checks['redis'] = {'status': 'error', 'error': str(e)}

        # Pending migrations
        try:
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            checks['migrations'] = {
                'status': 'ok' if not plan else 'pending',
                'pending': len(plan),
            }
        except Exception as e:
            checks['migrations'] = {'status': 'error', 'error': str(e)}

        overall = 'ok' if all(c.get('status') == 'ok' for c in checks.values()) else 'degraded'
        http_status = status.HTTP_200_OK if overall == 'ok' else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response({'status': overall, 'checks': checks}, status=http_status)


class DashboardStatsView(APIView):
    """
    GET /api/v1/dashboard/stats/
    Aggregated metrics for the current tenant's dashboard.
    All queries run inside the tenant schema — no cross-tenant risk.
    """
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get(self, request):
        from apps.contracts.models import Contract
        from apps.crm.models import Lead, UnitReservation
        from apps.inventory.models import Unit

        cache_key = f"{connection.schema_name}:dashboard:stats"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        # Inventory
        unit_qs = Unit.objects.all()
        inventory = {
            'total': unit_qs.count(),
            'available': unit_qs.filter(status=Unit.STATUS_AVAILABLE).count(),
            'reserved': unit_qs.filter(status=Unit.STATUS_RESERVED).count(),
            'contract': unit_qs.filter(status=Unit.STATUS_CONTRACT).count(),
            'sold': unit_qs.filter(status=Unit.STATUS_SOLD).count(),
        }

        # Revenue — sum of ACTIVE + COMPLETED contracts
        revenue_cve = (
            Contract.objects
            .filter(status__in=[Contract.STATUS_ACTIVE, Contract.STATUS_COMPLETED])
            .aggregate(total=Sum('total_price_cve'))['total'] or 0
        )

        # CRM pipeline counts by stage
        pipeline_qs = (
            Lead.objects
            .values('stage')
            .annotate(count=Count('id'))
            .order_by('stage')
        )
        pipeline = {item['stage']: item['count'] for item in pipeline_qs}

        # Reservations expiring in the next 24 hours
        expiring_soon = UnitReservation.objects.filter(
            status=UnitReservation.STATUS_ACTIVE,
            expires_at__lte=timezone.now() + timedelta(hours=24),
        ).count()

        # Contracts by status
        contracts_qs = (
            Contract.objects
            .values('status')
            .annotate(count=Count('id'))
        )
        contracts = {item['status']: item['count'] for item in contracts_qs}

        data = {
            'inventory': inventory,
            'revenue_cve': str(revenue_cve),
            'pipeline': pipeline,
            'reservations_expiring_soon': expiring_soon,
            'contracts': contracts,
        }
        cache.set(cache_key, data, timeout=30)
        return Response(data)
