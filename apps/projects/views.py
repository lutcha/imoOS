from rest_framework import viewsets, filters
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
