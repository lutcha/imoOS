from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Lead, Interaction
from .serializers import LeadSerializer, InteractionSerializer
from .filters import LeadFilter
from apps.users.permissions import IsTenantMember
from rest_framework.permissions import IsAuthenticated

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().select_related('assigned_to', 'interested_unit__floor__building__project')
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LeadFilter
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['created_at', 'budget', 'last_name']

    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        """
        Returns leads grouped by status for a Kanban-style pipeline view.
        """
        pipeline_data = {}
        for status_code, status_label in Lead.STATUS_CHOICES:
            leads = Lead.objects.filter(status=status_code)
            pipeline_data[status_code] = {
                'label': status_label,
                'count': leads.count(),
                'leads': LeadSerializer(leads[:50], many=True).data  # Limit to 50 per column for initial view
            }
        return Response(pipeline_data)

class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all().select_related('lead', 'created_by')
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lead', 'interaction_type', 'is_completed']
