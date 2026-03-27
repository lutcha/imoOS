from rest_framework import serializers
from .models import Lead, Interaction, UnitReservation


class LeadSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    unit_code = serializers.CharField(source='interested_unit.code', read_only=True)
    project_name = serializers.CharField(
        source='interested_unit.floor.building.project.name', read_only=True,
    )

    class Meta:
        model = Lead
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone',
            'status', 'stage', 'source',
            'budget', 'preferred_typology',
            'notes', 'lost_reason',
            'visit_date', 'proposal_sent_at', 'commission_rate',
            'assigned_to', 'assigned_to_name',
            'interested_unit', 'unit_code', 'project_name',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class PublicLeadSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for the unauthenticated LeadCaptureView.
    Exposes only contact/intent fields — no internal FK assignments.
    """
    class Meta:
        model = Lead
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone',
            'source', 'budget', 'preferred_typology', 'notes',
            'created_at',
        )
        read_only_fields = ('id', 'created_at')


class InteractionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Interaction
        fields = (
            'id', 'lead', 'interaction_type', 'date',
            'summary', 'is_completed', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ReservationSerializer(serializers.ModelSerializer):
    unit_code = serializers.CharField(source='unit.code', read_only=True)
    lead_name = serializers.SerializerMethodField()
    reserved_by_email = serializers.EmailField(source='reserved_by.email', read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = UnitReservation
        fields = (
            'id', 'unit', 'unit_code', 'lead', 'lead_name',
            'reserved_by', 'reserved_by_email',
            'status', 'is_active', 'expires_at',
            'deposit_amount_cve', 'notes',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'status', 'expires_at', 'reserved_by',
            'created_at', 'updated_at',
        )

    def get_lead_name(self, obj):
        return f'{obj.lead.first_name} {obj.lead.last_name}'


class CreateReservationSerializer(serializers.Serializer):
    unit_id = serializers.UUIDField()
    lead_id = serializers.UUIDField()
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    deposit_amount_cve = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, default='0.00',
    )
