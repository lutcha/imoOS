from django.db import connection
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.permissions import IsTenantMember
from .models import Unit, UnitType, UnitPricing, UnitOccurrence
from .serializers import (
    UnitSerializer, UnitTypeSerializer, UnitPricingSerializer, UnitOccurrenceSerializer
)
from .filters import UnitFilter

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.filter(is_deleted=False).select_related(
        'unit_type', 'floor', 'floor__building', 'floor__building__project'
    ).prefetch_related('pricing')
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UnitFilter
    search_fields = ['code', 'description']
    ordering_fields = ['code', 'area_bruta', 'created_at']

    def perform_create(self, serializer):
        from apps.tenants.models import TenantSettings
        from apps.tenants.limits import check_unit_limit
        tenant_settings, _ = TenantSettings.objects.get_or_create(
            tenant__schema_name=connection.schema_name,
            defaults={'tenant': self.request.tenant},
        )
        check = check_unit_limit(tenant_settings)
        if not check.allowed:
            raise ValidationError({'non_field_errors': [check.message]})
        serializer.save()

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        unit = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Unit.STATUS_CHOICES):
            return Response({'detail': 'Status inválido.'}, status=400)
        unit.status = new_status
        unit.save(update_fields=['status', 'updated_at'])
        return Response(UnitSerializer(unit).data)

    @action(
        detail=False,
        methods=['post'],
        url_path='import-csv',
        parser_classes=[MultiPartParser],
    )
    def import_csv(self, request):
        """
        Upload a CSV file to bulk-import Units asynchronously via Celery.
        """
        from .tasks import import_units_from_csv

        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'detail': 'Ficheiro CSV obrigatório.'}, status=400)
        if not csv_file.name.lower().endswith('.csv'):
            return Response({'detail': 'O ficheiro deve ter extensão .csv'}, status=400)
        if csv_file.size > MAX_UPLOAD_BYTES:
            return Response({'detail': 'Ficheiro demasiado grande (máximo 5 MB).'}, status=400)

        csv_content = csv_file.read().decode('utf-8-sig')

        task = import_units_from_csv.delay(
            tenant_schema=connection.schema_name,
            csv_content=csv_content,
            created_by_id=str(request.user.id),
        )
        return Response({'task_id': task.id, 'status': 'queued'}, status=202)


class UnitTypeViewSet(viewsets.ModelViewSet):
    queryset = UnitType.objects.all()
    serializer_class = UnitTypeSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]


class UnitOccurrenceViewSet(viewsets.ModelViewSet):
    queryset = UnitOccurrence.objects.all().select_related('unit', 'reported_by', 'assigned_to')
    serializer_class = UnitOccurrenceSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['unit', 'status', 'occurrence_type', 'priority']
    search_fields = ['description', 'unit__code']
    ordering_fields = ['created_at', 'priority', 'status']

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        from django.utils import timezone
        occurrence = self.get_object()
        occurrence.status = UnitOccurrence.STATUS_RESOLVED
        occurrence.resolved_at = timezone.now()
        occurrence.save(update_fields=['status', 'resolved_at', 'updated_at'])
        return Response(UnitOccurrenceSerializer(occurrence).data)
