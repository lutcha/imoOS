from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Unit
from .serializers import UnitSerializer
from apps.users.permissions import IsTenantMember
from rest_framework.permissions import IsAuthenticated

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all().select_related('floor__building__project')
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'unit_type', 'floor', 'floor__building', 'floor__building__project']
    search_fields = ['number', 'fraçao']
    ordering_fields = ['price', 'number', 'created_at']

    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        unit = self.get_object()
        if unit.status != Unit.STATUS_AVAILABLE:
            return Response({'error': 'Unit is not available for reservation.'}, status=status.HTTP_400_BAD_REQUEST)
        
        unit.status = Unit.STATUS_RESERVED
        unit.save()
        return Response(self.get_serializer(unit).data)

    @action(detail=True, methods=['post'])
    def sell(self, request, pk=None):
        unit = self.get_object()
        if unit.status not in [Unit.STATUS_AVAILABLE, Unit.STATUS_RESERVED]:
            return Response({'error': 'Unit must be available or reserved to be sold.'}, status=status.HTTP_400_BAD_REQUEST)
        
        unit.status = Unit.STATUS_SOLD
        unit.save()
        return Response(self.get_serializer(unit).data)
