import os
import re
import uuid
import logging
from django.db.models import Count

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django_tenants.utils import schema_context
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsTenantMember
from .models import Client, Domain, PlanEvent, TenantSettings
from .permissions import IsTenantAdmin
from .serializers import (
    ClientCreateSerializer,
    ClientSerializer,
    TenantSettingsSerializer,
    TenantSettingsWritableSerializer,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Super-Admin Platform API — manage all tenants (Sprint 7)
# ---------------------------------------------------------------------------

class TenantAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for super-admin tenant management.
    Includes usage counts from each tenant schema.
    """
    domain = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()
    project_count = serializers.SerializerMethodField()
    unit_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'name', 'slug', 'schema_name', 'plan', 'is_active',
            'country', 'currency', 'timezone', 'created_at', 'updated_at',
            'domain', 'user_count', 'project_count', 'unit_count',
        ]
        read_only_fields = fields

    def get_domain(self, obj):
        domain = obj.domains.filter(is_primary=True).first()
        return domain.domain if domain else None

    def get_user_count(self, obj):
        """Count users in tenant schema."""
        try:
            with schema_context(obj.schema_name):
                from django.contrib.auth import get_user_model
                User = get_user_model()
                return User.objects.count()
        except Exception:
            return 0

    def get_project_count(self, obj):
        """Count projects in tenant schema."""
        try:
            with schema_context(obj.schema_name):
                from apps.projects.models import Project
                return Project.objects.count()
        except Exception:
            return 0

    def get_unit_count(self, obj):
        """Count units in tenant schema."""
        try:
            with schema_context(obj.schema_name):
                from apps.inventory.models import Unit
                return Unit.objects.count()
        except Exception:
            return 0


class SuperAdminTenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Super-admin view for managing all tenants.
    Requires is_staff=True. Always operates on public schema.
    
    Endpoints:
    - GET /api/v1/superadmin/tenants/ — list all tenants with usage counts
    - GET /api/v1/superadmin/tenants/{id}/ — tenant details
    - POST /api/v1/superadmin/tenants/{id}/suspend/ — suspend tenant
    - POST /api/v1/superadmin/tenants/{id}/activate/ — activate tenant
    - GET /api/v1/superadmin/tenants/platform_summary/ — aggregated metrics
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = TenantAdminSerializer
    queryset = (
        Client.objects
        .select_related('settings')
        .prefetch_related('domains')
        .order_by('-created_at')
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['plan', 'is_active', 'country']
    search_fields = ['name', 'slug', 'schema_name']
    ordering_fields = ['name', 'created_at', 'plan']

    @action(detail=False, methods=['get'])
    def platform_summary(self, request):
        """
        Aggregated platform metrics for super-admin dashboard.
        Returns counts by plan, active/inactive tenants, total resources.
        """
        # Basic counts (public schema)
        total_tenants = Client.objects.count()
        active_tenants = Client.objects.filter(is_active=True).count()
        
        # Count by plan
        tenants_by_plan = dict(
            Client.objects
            .values_list('plan')
            .annotate(count=Count('id'))
            .values_list('plan', 'count')
        )
        
        # Aggregate resources across all tenants
        total_projects = 0
        total_units = 0
        total_users = 0
        
        for tenant in Client.objects.filter(is_active=True):
            try:
                with schema_context(tenant.schema_name):
                    from apps.projects.models import Project
                    from apps.inventory.models import Unit
                    from django.contrib.auth import get_user_model
                    
                    total_projects += Project.objects.count()
                    total_units += Unit.objects.count()
                    User = get_user_model()
                    total_users += User.objects.count()
            except Exception:
                logger.warning(f'Failed to count resources for tenant {tenant.schema_name}')
        
        return Response({
            'total_tenants': total_tenants,
            'active_tenants': active_tenants,
            'inactive_tenants': total_tenants - active_tenants,
            'tenants_by_plan': tenants_by_plan,
            'total_resources': {
                'projects': total_projects,
                'units': total_units,
                'users': total_users,
            },
        })

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Suspend a tenant (soft delete)."""
        tenant = self.get_object()
        tenant.is_active = False
        tenant.save(update_fields=['is_active', 'updated_at'])
        
        # Log the action
        PlanEvent.objects.create(
            tenant=tenant,
            event_type=PlanEvent.EVENT_LIMIT_HIT,
            from_plan=tenant.plan,
            to_plan=tenant.plan,
            metadata={'action': 'suspended', 'by': request.user.email},
            created_by=request.user,
        )
        
        return Response({'status': 'suspended', 'id': str(tenant.id)})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a suspended tenant."""
        tenant = self.get_object()
        tenant.is_active = True
        tenant.save(update_fields=['is_active', 'updated_at'])
        
        return Response({'status': 'activated', 'id': str(tenant.id)})


# ---------------------------------------------------------------------------
# Platform-level admin: manage all tenants
# ---------------------------------------------------------------------------

class TenantViewSet(viewsets.ModelViewSet):
    """
    Platform admin CRUD for tenants (Client + Domain + TenantSettings).
    Restricted to staff users (is_staff=True) only.
    Client lives in the public schema so queries are always schema-safe.
    """
    queryset = (
        Client.objects
        .prefetch_related('domains')
        .select_related('settings')
        .order_by('name')
    )
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['plan', 'is_active', 'country']
    search_fields = ['name', 'slug', 'schema_name']
    ordering_fields = ['name', 'created_at', 'plan']

    def get_serializer_class(self):
        if self.action == 'create':
            return ClientCreateSerializer
        return ClientSerializer

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Re-activate a suspended tenant."""
        tenant = self.get_object()
        tenant.is_active = True
        tenant.save(update_fields=['is_active', 'updated_at'])
        return Response({'status': 'activated', 'id': str(tenant.id)})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Suspend a tenant — blocks schema access via ImoOSTenantMiddleware."""
        tenant = self.get_object()
        tenant.is_active = False
        tenant.save(update_fields=['is_active', 'updated_at'])
        return Response({'status': 'deactivated', 'id': str(tenant.id)})

    @action(detail=True, methods=['patch'], url_path='plan-limits')
    def plan_limits(self, request, pk=None):
        """Staff-only override of plan limits (max_projects, max_units, max_users)."""
        tenant = self.get_object()
        settings_obj, _ = TenantSettings.objects.get_or_create(tenant=tenant)
        serializer = TenantSettingsWritableSerializer(
            settings_obj, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Tenant-scoped: current tenant's settings (branding + config)
# ---------------------------------------------------------------------------

class TenantSettingsView(generics.RetrieveUpdateAPIView):
    """
    Read/update branding and integration settings for the current tenant.
    GET: any authenticated tenant member.
    PATCH/PUT: tenant admin role required.
    """
    serializer_class = TenantSettingsSerializer

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [IsAuthenticated(), IsTenantMember()]
        return [IsAuthenticated(), IsTenantAdmin()]

    def get_object(self):
        settings_obj, _ = TenantSettings.objects.get_or_create(tenant=self.request.tenant)
        return settings_obj


# ---------------------------------------------------------------------------
# Tenant usage / plan consumption
# ---------------------------------------------------------------------------

class UsageView(APIView):
    """
    GET /api/v1/tenant/usage/

    Returns current resource usage vs plan limits for the active tenant.
    Response shape:
        {
            "plan": "starter",
            "projects": {"current": 2, "limit": 3, "pct_used": 67},
            "units":    {"current": 40, "limit": 100, "pct_used": 40},
            "users":    {"current": 4,  "limit": 5,  "pct_used": 80}
        }
    """
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get(self, request):
        from django.db import connection
        from apps.tenants.limits import check_project_limit, check_unit_limit, check_user_limit

        tenant_settings, _ = TenantSettings.objects.get_or_create(tenant=request.tenant)

        return Response({
            'plan': request.tenant.plan,
            'projects': check_project_limit(tenant_settings).as_dict(),
            'units': check_unit_limit(tenant_settings).as_dict(),
            'users': check_user_limit(tenant_settings).as_dict(),
        })


class PlanEventsView(APIView):
    """
    GET /api/v1/tenant/plan-events/

    Lists plan lifecycle events for the current tenant (staff or tenant admin).
    """
    permission_classes = [IsAuthenticated, IsTenantMember]

    def get(self, request):
        events = PlanEvent.objects.filter(tenant=request.tenant).order_by('-created_at')[:50]
        data = [
            {
                'id': str(e.id),
                'event_type': e.event_type,
                'from_plan': e.from_plan,
                'to_plan': e.to_plan,
                'metadata': e.metadata,
                'created_at': e.created_at.isoformat(),
            }
            for e in events
        ]
        return Response(data)


# ---------------------------------------------------------------------------
# S3 presigned upload URL
# ---------------------------------------------------------------------------

def _sanitize_filename(filename: str) -> str:
    """Strip path traversal and unsafe characters, preserve extension."""
    filename = os.path.basename(filename)            # no directory traversal
    filename = re.sub(r'[^\w.\-]', '_', filename)   # allow word chars, dots, hyphens
    filename = re.sub(r'^\.+', '', filename)         # no leading dots (hidden files)
    return filename or 'upload'


class S3PresignedUploadView(APIView):
    """
    Generate a presigned S3 PUT URL for direct browser-to-S3 uploads.

    POST body:
        filename       — original filename (sanitised server-side)
        resource_type  — one of ALLOWED_RESOURCE_TYPES
        content_type   — MIME type of the file

    Response:
        upload_url  — presigned PUT URL (valid for EXPIRY_SECONDS)
        key         — S3 object key to pass back after upload
        expires_in  — seconds until URL expires
    """
    permission_classes = [IsAuthenticated, IsTenantMember]

    ALLOWED_RESOURCE_TYPES = frozenset({
        'unit_photos', 'documents', 'branding', 'construction',
    })
    ALLOWED_CONTENT_TYPES = frozenset({
        'image/jpeg', 'image/png', 'image/webp', 'image/gif',
        'application/pdf',
        'video/mp4',
    })
    EXPIRY_SECONDS = 300

    def post(self, request):
        filename = request.data.get('filename', '').strip()
        resource_type = request.data.get('resource_type', '')
        content_type = request.data.get('content_type', '')

        errors = {}
        if not filename:
            errors['filename'] = 'This field is required.'
        if resource_type not in self.ALLOWED_RESOURCE_TYPES:
            errors['resource_type'] = (
                f'Must be one of: {", ".join(sorted(self.ALLOWED_RESOURCE_TYPES))}.'
            )
        if content_type not in self.ALLOWED_CONTENT_TYPES:
            errors['content_type'] = (
                f'Must be one of: {", ".join(sorted(self.ALLOWED_CONTENT_TYPES))}.'
            )
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        if not settings.AWS_ACCESS_KEY_ID:
            return Response(
                {'detail': 'S3 storage not configured in this environment.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        safe_name = _sanitize_filename(filename)
        tenant = request.tenant
        key = f'tenants/{tenant.slug}/{resource_type}/{uuid.uuid4()}/{safe_name}'

        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL or None,
                region_name='us-east-1',
            )
            upload_url = s3.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': key,
                    'ContentType': content_type,
                },
                ExpiresIn=self.EXPIRY_SECONDS,
            )
        except ClientError as exc:
            logger.error('S3 presigned URL generation failed: %s', exc)
            return Response(
                {'detail': 'Could not generate upload URL. Try again later.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({
            'upload_url': upload_url,
            'key': key,
            'expires_in': self.EXPIRY_SECONDS,
        }, status=status.HTTP_200_OK)
