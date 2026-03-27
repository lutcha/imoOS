from django.db import connection
from rest_framework import viewsets, filters
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Building, Floor
from .serializers import ProjectSerializer, BuildingSerializer, FloorSerializer
from apps.users.permissions import IsTenantMember
from rest_framework.permissions import IsAuthenticated


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().prefetch_related('buildings')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'city']
    search_fields = ['name', 'address', 'city']
    ordering_fields = ['created_at', 'name', 'expected_delivery_date']

    def perform_create(self, serializer):
        from apps.tenants.models import TenantSettings
        from apps.tenants.limits import check_project_limit
        tenant_settings, _ = TenantSettings.objects.get_or_create(
            tenant__schema_name=connection.schema_name,
            defaults={'tenant': self.request.tenant},
        )
        check = check_project_limit(tenant_settings)
        if not check.allowed:
            raise ValidationError({'non_field_errors': [check.message]})
        serializer.save()

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all().prefetch_related('floors')
    serializer_class = BuildingSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project']
    search_fields = ['name']

class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.all().prefetch_related('units')
    serializer_class = FloorSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['building']
