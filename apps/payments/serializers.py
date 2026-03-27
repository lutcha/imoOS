from rest_framework import serializers

from .models import PaymentPlan, PaymentPlanItem


class PaymentPlanItemSerializer(serializers.ModelSerializer):
    is_paid = serializers.BooleanField(read_only=True)
    item_type_display = serializers.CharField(source='get_item_type_display', read_only=True)
    # Mirror the linked payment status for convenience (null if not yet paid)
    payment_status = serializers.CharField(
        source='payment.status', default=None, read_only=True
    )
    payment_paid_date = serializers.DateField(
        source='payment.paid_date', default=None, read_only=True
    )

    class Meta:
        model = PaymentPlanItem
        fields = (
            'id',
            'item_type',
            'item_type_display',
            'percentage',
            'amount_cve',
            'due_date',
            'order',
            'mbe_reference',
            'is_paid',
            'payment',
            'payment_status',
            'payment_paid_date',
            'created_at',
        )
        read_only_fields = (
            'id',
            'item_type_display',
            'is_paid',
            'payment_status',
            'payment_paid_date',
            'created_at',
        )


class PaymentPlanSerializer(serializers.ModelSerializer):
    items = PaymentPlanItemSerializer(many=True, read_only=True)
    plan_type_display = serializers.CharField(source='get_plan_type_display', read_only=True)
    contract_number = serializers.CharField(source='contract.contract_number', read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    paid_count = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = (
            'id',
            'contract',
            'contract_number',
            'plan_type',
            'plan_type_display',
            'total_cve',
            'notes',
            'items_count',
            'paid_count',
            'items',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'contract_number',
            'plan_type_display',
            'items_count',
            'paid_count',
            'items',
            'created_at',
            'updated_at',
        )

    def get_paid_count(self, obj) -> int:
        return obj.items.filter(payment__isnull=False).count()


class GeneratePlanSerializer(serializers.Serializer):
    installments = serializers.IntegerField(
        min_value=1,
        max_value=360,
        default=8,
        help_text='Número de prestações mensais (padrão: 8)',
    )
    start_date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text='Data base do plano (omitir = usar data de assinatura do contrato ou hoje)',
    )
