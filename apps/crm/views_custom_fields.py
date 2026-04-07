"""
Custom Fields API for CRM
"""
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsTenantAdmin
from .models_custom_fields import CustomFieldDefinition, LeadCustomValue


class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFieldDefinition
        fields = ['id', 'name', 'key', 'field_type', 'required', 'help_text', 'choices', 'order', 'is_active']


class CustomFieldViewSet(viewsets.ModelViewSet):
    """
    Manage custom field definitions (admin only).
    """
    serializer_class = CustomFieldSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    
    def get_queryset(self):
        return CustomFieldDefinition.objects.filter(is_active=True).order_by('order', 'name')
    
    @action(detail=False, methods=['get'])
    def for_lead(self, request):
        """Get all custom fields available for leads."""
        fields = self.get_queryset()
        return Response(self.serializer_class(fields, many=True).data)


class LeadCustomValueSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='field.name', read_only=True)
    field_type = serializers.CharField(source='field.field_type', read_only=True)
    
    class Meta:
        model = LeadCustomValue
        fields = ['id', 'field', 'field_name', 'field_type', 'value']
    
    def get_value(self, obj):
        return obj.value


class LeadCustomValueViewSet(viewsets.ModelViewSet):
    """
    Manage custom field values for leads.
    """
    serializer_class = LeadCustomValueSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        lead_id = self.request.query_params.get('lead')
        if lead_id:
            return LeadCustomValue.objects.filter(lead_id=lead_id)
        return LeadCustomValue.objects.none()
    
    def create(self, request, *args, **kwargs):
        # Handle bulk creation/update
        data = request.data
        if isinstance(data, list):
            return self._bulk_update(request, data)
        return super().create(request, *args, **kwargs)
    
    def _bulk_update(self, request, data):
        """Update multiple custom values at once."""
        results = []
        for item in data:
            lead_id = item.get('lead')
            field_id = item.get('field')
            value = item.get('value')
            
            try:
                custom_value, created = LeadCustomValue.objects.update_or_create(
                    lead_id=lead_id,
                    field_id=field_id,
                    defaults={'tenant': request.tenant},
                )
                custom_value.set_value(value)
                custom_value.save()
                results.append({
                    'id': str(custom_value.id),
                    'success': True,
                    'created': created
                })
            except Exception as e:
                results.append({
                    'field': field_id,
                    'success': False,
                    'error': str(e)
                })
        
        return Response(results, status=status.HTTP_200_OK)
