"""
PaymentPlan ViewSet — ImoOS

Read operations:  IsTenantMember
Write operations: IsTenantAdmin
generate / regenerate actions: IsTenantAdmin

All queries are automatically scoped to the active tenant schema by
django-tenants middleware — no explicit cross-schema filtering needed.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tenants.permissions import IsTenantAdmin
from apps.users.permissions import IsTenantMember

from .models import PaymentPlan
from .serializers import GeneratePlanSerializer, PaymentPlanSerializer


class PaymentPlanViewSet(viewsets.ModelViewSet):
    """
    CRUD for PaymentPlan.
    - list / retrieve: IsTenantMember
    - create / update / destroy / generate / regenerate: IsTenantAdmin

    Filtering:
      ?contract=<uuid>
    """

    serializer_class = PaymentPlanSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['contract', 'plan_type']
    ordering_fields = ['created_at', 'total_cve']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsTenantMember()]
        return [IsAuthenticated(), IsTenantAdmin()]

    def get_queryset(self):
        return (
            PaymentPlan.objects
            .select_related('contract')
            .prefetch_related('items__payment')
            .order_by('-created_at')
        )

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """
        POST /api/v1/payments/plans/generate/
        Body: { "contract": "<uuid>", "installments": 8, "start_date": "YYYY-MM-DD" (opt) }

        Creates (or returns existing) a PaymentPlan for the contract and generates
        standard plan items. Idempotent: re-posting regenerates items.
        """
        # Validate contract field
        contract_id = request.data.get('contract')
        if not contract_id:
            return Response({'contract': 'Este campo é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.contracts.models import Contract
        try:
            contract = Contract.objects.get(id=contract_id)
        except Contract.DoesNotExist:
            return Response({'contract': 'Contrato não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        gen_serializer = GeneratePlanSerializer(data=request.data)
        gen_serializer.is_valid(raise_exception=True)
        installments = gen_serializer.validated_data['installments']
        start_date = gen_serializer.validated_data.get('start_date')

        plan, _ = PaymentPlan.objects.get_or_create(
            contract=contract,
            defaults={'total_cve': contract.total_price_cve, 'plan_type': PaymentPlan.TYPE_STANDARD},
        )
        # Ensure total_cve stays in sync if contract price changed
        if plan.total_cve != contract.total_price_cve:
            plan.total_cve = contract.total_price_cve
            plan.save(update_fields=['total_cve', 'updated_at'])

        plan.generate_standard(installments=installments, start_date=start_date)

        serializer = PaymentPlanSerializer(plan, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='regenerate')
    def regenerate(self, request, pk=None):
        """
        POST /api/v1/payments/plans/{id}/regenerate/
        Body: { "installments": 8 (opt), "start_date": "YYYY-MM-DD" (opt) }

        Deletes all existing items and regenerates the standard schedule.
        Useful when the contract value or start date changes.
        """
        plan = self.get_object()

        gen_serializer = GeneratePlanSerializer(data=request.data)
        gen_serializer.is_valid(raise_exception=True)
        installments = gen_serializer.validated_data['installments']
        start_date = gen_serializer.validated_data.get('start_date')

        # Sync total with contract in case it was updated
        plan.total_cve = plan.contract.total_price_cve
        plan.save(update_fields=['total_cve', 'updated_at'])

        plan.generate_standard(installments=installments, start_date=start_date)

        serializer = PaymentPlanSerializer(plan, context={'request': request})
        return Response(serializer.data)
