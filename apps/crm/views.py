from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsTenantMember
from .filters import LeadFilter
from .models import Lead, Interaction, UnitReservation
from .serializers import (
    CreateReservationSerializer,
    InteractionSerializer,
    LeadSerializer,
    ReservationSerializer,
)
from .services import (
    ActiveReservationExistsError,
    UnitNotAvailableError,
    advance_lead_stage,
    cancel_reservation,
    convert_reservation,
    create_reservation,
)


class LeadViewSet(viewsets.ModelViewSet):
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LeadFilter
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['created_at', 'budget', 'last_name', 'stage']

    def get_queryset(self):
        return (
            Lead.objects
            .select_related('assigned_to', 'interested_unit__floor__building__project')
            .order_by('-created_at')
        )

    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        """Leads grouped by stage for the Kanban board."""
        pipeline_data = {}
        for stage_code, stage_label in Lead.STAGE_CHOICES:
            qs = Lead.objects.filter(stage=stage_code)
            pipeline_data[stage_code] = {
                'label': stage_label,
                'count': qs.count(),
                'leads': LeadSerializer(qs.select_related('assigned_to')[:50], many=True).data,
            }
        return Response(pipeline_data)

    @action(detail=True, methods=['patch'], url_path='move-stage')
    def move_stage(self, request, pk=None):
        """
        Move a lead to the next pipeline stage (Kanban drag-and-drop).
        Body: {"stage": "proposal_sent", "lost_reason": "..."}
        Uses advance_lead_stage() — validates allowed transitions.
        """
        lead = self.get_object()
        new_stage = request.data.get('stage')
        lost_reason = request.data.get('lost_reason', '')

        if not new_stage:
            return Response({'stage': 'Este campo é obrigatório.'}, status=400)

        lead = advance_lead_stage(str(lead.id), new_stage, request.user, lost_reason)
        return Response(LeadSerializer(lead).data)

    @action(detail=True, methods=['post'], url_path='schedule-visit')
    def schedule_visit(self, request, pk=None):
        """
        Record a scheduled visit date and advance stage to visit_scheduled.
        Body: {"visit_date": "2026-04-10T10:00:00Z"}
        """
        lead = self.get_object()
        visit_date = request.data.get('visit_date')
        if not visit_date:
            return Response({'visit_date': 'Este campo é obrigatório.'}, status=400)

        lead.visit_date = visit_date
        lead.save(update_fields=['visit_date', 'updated_at'])

        # Only advance if the stage allows it
        from .models import LEAD_STAGE_TRANSITIONS
        if 'visit_scheduled' in LEAD_STAGE_TRANSITIONS.get(lead.stage, []):
            lead = advance_lead_stage(str(lead.id), Lead.STAGE_VISIT_SCHEDULED, request.user)

        return Response(LeadSerializer(lead).data)

    @action(detail=True, methods=['post'], url_path='send-proposal')
    def send_proposal(self, request, pk=None):
        """
        Trigger async PDF generation and record proposal_sent_at.
        Body: {"unit_id": "<uuid>"}
        The Celery task uploads the PDF to S3 and returns the key.
        """
        lead = self.get_object()
        unit_id = request.data.get('unit_id')
        if not unit_id:
            return Response({'unit_id': 'Este campo é obrigatório.'}, status=400)

        from .tasks import generate_proposal_pdf
        task = generate_proposal_pdf.delay(
            tenant_schema=request.tenant.schema_name,
            lead_id=str(lead.id),
            unit_id=str(unit_id),
        )

        lead.proposal_sent_at = timezone.now()
        lead.save(update_fields=['proposal_sent_at', 'updated_at'])

        if 'proposal_sent' in __import__('apps.crm.models', fromlist=['LEAD_STAGE_TRANSITIONS']).LEAD_STAGE_TRANSITIONS.get(lead.stage, []):
            advance_lead_stage(str(lead.id), Lead.STAGE_PROPOSAL_SENT, request.user)

        return Response({'task_id': task.id, 'proposal_sent_at': lead.proposal_sent_at})


class ReservationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List/retrieve reservations (read-only).
    Mutations go through dedicated actions to enforce business rules.
    """
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'unit', 'lead']
    ordering_fields = ['created_at', 'expires_at']

    def get_queryset(self):
        return (
            UnitReservation.objects
            .select_related('unit', 'lead', 'reserved_by')
            .order_by('-created_at')
        )

    @action(detail=False, methods=['post'], url_path='create-reservation')
    def create_reservation(self, request):
        """
        Create a reservation with SELECT FOR UPDATE — prevents double-booking.
        Body: {"unit_id": "<uuid>", "lead_id": "<uuid>", "notes": "", "deposit_amount_cve": 0}
        """
        serializer = CreateReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        try:
            reservation = create_reservation(
                unit_id=str(d['unit_id']),
                lead_id=str(d['lead_id']),
                user=request.user,
                notes=d.get('notes', ''),
                deposit_cve=d.get('deposit_amount_cve', '0.00'),
            )
        except (UnitNotAvailableError, ActiveReservationExistsError) as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)

        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an active reservation and release the unit back to AVAILABLE.
        """
        reservation = self.get_object()
        try:
            reservation = cancel_reservation(str(reservation.id), request.user)
        except Exception as exc:
            return Response(
                getattr(exc, 'detail', str(exc)),
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(ReservationSerializer(reservation).data)

    @action(detail=True, methods=['post'], url_path='convert-to-contract')
    def convert_to_contract(self, request, pk=None):
        """
        Mark reservation as CONVERTED and transition unit to CONTRACT status.
        Called by the contracts module when a contract is signed.
        """
        reservation = self.get_object()
        try:
            reservation = convert_reservation(str(reservation.id), request.user)
        except Exception as exc:
            return Response(
                getattr(exc, 'detail', str(exc)),
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(ReservationSerializer(reservation).data)


class InteractionViewSet(viewsets.ModelViewSet):
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lead', 'interaction_type', 'is_completed']

    def get_queryset(self):
        return Interaction.objects.select_related('lead', 'created_by').order_by('-date')
