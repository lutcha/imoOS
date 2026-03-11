from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


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
