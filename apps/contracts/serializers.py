from datetime import date

from rest_framework import serializers

from .models import Contract, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'id',
            'contract',
            'payment_type',
            'amount_cve',
            'due_date',
            'paid_date',
            'status',
            'reference',
            'created_at',
        )
        read_only_fields = ('id', 'created_at')


class ContractSerializer(serializers.ModelSerializer):
    unit_code = serializers.CharField(source='unit.code', read_only=True)
    lead_name = serializers.SerializerMethodField()
    vendor_email = serializers.EmailField(source='vendor.email', read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = (
            'id',
            'reservation',
            'unit',
            'unit_code',
            'lead',
            'lead_name',
            'vendor',
            'vendor_email',
            'status',
            'contract_number',
            'total_price_cve',
            'signed_at',
            'pdf_s3_key',
            'notes',
            'payments',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'contract_number',
            'unit_code',
            'lead_name',
            'vendor_email',
            'pdf_s3_key',
            'payments',
            'created_at',
            'updated_at',
        )

    def get_lead_name(self, obj):
        return obj.lead.full_name if hasattr(obj.lead, 'full_name') else (
            f'{obj.lead.first_name} {obj.lead.last_name}'
        )


class ContractCreateSerializer(serializers.Serializer):
    reservation_id = serializers.UUIDField()
    unit_id = serializers.UUIDField()
    lead_id = serializers.UUIDField()
    total_price_cve = serializers.DecimalField(max_digits=14, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_reservation_id(self, value):
        from apps.crm.models import UnitReservation
        try:
            reservation = UnitReservation.objects.get(id=value)
        except UnitReservation.DoesNotExist:
            raise serializers.ValidationError('Reserva não encontrada.')
        if reservation.status != UnitReservation.STATUS_ACTIVE:
            raise serializers.ValidationError(
                f'Reserva não está activa (estado actual: {reservation.get_status_display()}).'
            )
        return value


class PaymentMarkPaidSerializer(serializers.Serializer):
    paid_date = serializers.DateField(default=date.today)
    reference = serializers.CharField(required=False, allow_blank=True, default='')


class GeneratePaymentPlanSerializer(serializers.Serializer):
    deposit_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=True)
    final_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=True)
    installments_count = serializers.IntegerField(min_value=0, required=True)
    start_date = serializers.DateField(required=True)
    
    def validate(self, data):
        if data['deposit_percentage'] + data['final_percentage'] > 100:
            raise serializers.ValidationError("A soma da percentagem de sinal e final não pode exceder 100%.")
        return data
