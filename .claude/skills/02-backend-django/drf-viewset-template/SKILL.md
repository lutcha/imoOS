---
name: drf-viewset-template
description: Generate DRF ViewSets with tenant isolation, RBAC permissions, filtering, pagination, and audit logging for ImoOS. Auto-load when creating any API endpoint.
argument-hint: [ModelName] [crud-operations]
allowed-tools: Read, Write, Grep
---

# DRF ViewSet Template — ImoOS

## Standard ViewSet Pattern

```python
# apps/<module>/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.permissions import IsTenantMember, IsTenantAdmin
from apps.core.pagination import StandardResultsPagination
from apps.<module>.models import <Model>
from apps.<module>.serializers import <Model>Serializer, <Model>CreateSerializer
from apps.<module>.filters import <Model>Filter
from apps.<module>.services import <Model>Service


class <Model>ViewSet(viewsets.ModelViewSet):
    """
    CRUD for <Model>. All operations are tenant-scoped.
    Requires: authenticated user + tenant membership.
    """
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = <Model>Serializer
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = <Model>Filter
    search_fields = ['name', 'code']          # Adjust per model
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        # django-tenants middleware auto-scopes to active tenant schema
        return <Model>.objects.select_related('project').filter(
            is_deleted=False
        )

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return <Model>CreateSerializer
        return <Model>Serializer

    def get_permissions(self):
        if self.action in ['destroy', 'bulk_delete']:
            return [IsAuthenticated(), IsTenantAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete — never hard delete business records
        instance.is_deleted = True
        instance.deleted_by = self.request.user
        instance.save()

    @action(detail=False, methods=['post'], url_path='bulk-import')
    def bulk_import(self, request):
        """Import multiple records via CSV. Runs as Celery task."""
        from apps.<module>.tasks import bulk_import_<model>
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)

        task = bulk_import_<model>.delay(
            tenant_id=str(request.tenant.id),
            file_content=file.read().decode('utf-8'),
            user_id=str(request.user.id),
        )
        return Response({'task_id': task.id}, status=202)
```

## URL Registration
```python
# apps/<module>/urls.py
from rest_framework.routers import DefaultRouter
from apps.<module>.views import <Model>ViewSet

router = DefaultRouter()
router.register(r'<model-plural>', <Model>ViewSet, basename='<model>')

urlpatterns = router.urls
```

## Required Additions per ViewSet
1. `filterset_class` — define in `filters.py`
2. `select_related` / `prefetch_related` — avoid N+1 queries
3. Soft delete pattern (never `instance.delete()` for business records)
4. Audit log on create/update/delete via signal or service layer
