from rest_framework import serializers
from .models import Lead, Interaction
from apps.users.serializers import UserSerializer

class LeadSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    unit_number = serializers.CharField(source='interested_unit.number', read_only=True)
    project_name = serializers.CharField(source='interested_unit.floor.building.project.name', read_only=True)

    class Meta:
        model = Lead
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone', 
            'status', 'source', 'budget', 'preferred_typology', 
            'notes', 'assigned_to', 'assigned_to_name', 
            'interested_unit', 'unit_number', 'project_name',
            'created_at', 'updated_at'
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
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
