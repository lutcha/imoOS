from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.permissions import IsTenantMember
from .models import Unit, UnitType, UnitPricing
from .serializers import UnitSerializer, UnitTypeSerializer, UnitPricingSerializer
from .filters import UnitFilter


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

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        unit = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Unit.STATUS_CHOICES):
            return Response({'detail': 'Status inválido.'}, status=400)
        unit.status = new_status
        unit.save(update_fields=['status', 'updated_at'])
        return Response(UnitSerializer(unit).data)


class UnitTypeViewSet(viewsets.ModelViewSet):
    queryset = UnitType.objects.all()
    serializer_class = UnitTypeSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
