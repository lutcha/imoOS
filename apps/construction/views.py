from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.users.permissions import IsTenantMember

from .filters import DailyReportFilter
from .models import ConstructionPhoto, ConstructionProgress, DailyReport
from .permissions import IsEngineerOrAdmin
from .serializers import (
    ConstructionPhotoSerializer,
    ConstructionProgressSerializer,
    DailyReportSerializer,
)


class DailyReportViewSet(viewsets.ModelViewSet):
    serializer_class = DailyReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DailyReportFilter
    search_fields = ['summary', 'weather']
    ordering_fields = ['date', 'progress_pct', 'created_at']

    def get_queryset(self):
        return (
            DailyReport.objects.select_related('project', 'building', 'author')
            .prefetch_related('photos')
            .order_by('-date')
        )

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'submit', 'approve'):
            return [IsAuthenticated(), IsEngineerOrAdmin()]
        return [IsAuthenticated(), IsTenantMember()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Transition a DailyReport from DRAFT to SUBMITTED."""
        report = self.get_object()
        if report.status != DailyReport.STATUS_DRAFT:
            return Response(
                {'detail': 'Apenas relatórios em rascunho podem ser submetidos.'},
                status=400,
            )
        report.status = DailyReport.STATUS_SUBMITTED
        report.save(update_fields=['status', 'updated_at'])
        return Response(DailyReportSerializer(report).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Transition a DailyReport from SUBMITTED to APPROVED (admin only).

        After approval, the ConstructionProgress snapshot for the building is
        updated via update_or_create so the frontend always has an up-to-date
        completion percentage.
        """
        from apps.memberships.models import TenantMembership

        try:
            membership = TenantMembership.objects.get(user=request.user)
        except TenantMembership.DoesNotExist:
            return Response({'detail': 'Sem permissão para aprovar relatórios.'}, status=403)

        if not membership.is_admin:
            return Response({'detail': 'Apenas administradores podem aprovar relatórios.'}, status=403)

        report = self.get_object()
        if report.status != DailyReport.STATUS_SUBMITTED:
            return Response(
                {'detail': 'Apenas relatórios submetidos podem ser aprovados.'},
                status=400,
            )

        report.status = DailyReport.STATUS_APPROVED
        report.save(update_fields=['status', 'updated_at'])

        if report.building_id:
            ConstructionProgress.objects.update_or_create(
                building=report.building,
                defaults={
                    'progress_pct': report.progress_pct,
                    'last_report': report,
                },
            )

        return Response(DailyReportSerializer(report).data)


class ConstructionPhotoViewSet(viewsets.ModelViewSet):
    serializer_class = ConstructionPhotoSerializer
    permission_classes = [IsAuthenticated, IsEngineerOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report']

    def get_queryset(self):
        qs = ConstructionPhoto.objects.select_related('report', 'created_by').order_by(
            '-created_at'
        )
        report_id = self.request.query_params.get('report__id')
        if report_id:
            qs = qs.filter(report__id=report_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
