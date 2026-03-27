"""
Investor Portal views — read-only access to contracts and payments
scoped to the authenticated investor's email.
"""
import logging
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsTenantMember, IsInvestorOrAdmin

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

class PaymentSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    contract_number = serializers.CharField(source='contract.contract_number')
    unit_code = serializers.CharField(source='contract.unit.code')
    payment_type = serializers.CharField()
    amount_cve = serializers.DecimalField(max_digits=14, decimal_places=2)
    due_date = serializers.DateField()
    status = serializers.CharField()


class ContractSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    contract_number = serializers.CharField()
    unit_code = serializers.CharField(source='unit.code')
    project_name = serializers.CharField(source='unit.floor.building.project.name')
    status = serializers.CharField()
    total_price_cve = serializers.DecimalField(max_digits=14, decimal_places=2)
    signed_at = serializers.DateTimeField(allow_null=True)
    pdf_s3_key = serializers.CharField()


# ---------------------------------------------------------------------------
# ViewSet
# ---------------------------------------------------------------------------

class InvestorPortalViewSet(viewsets.ViewSet):
    """
    Read-only portal for investors and admins.

    Investors see only their own contracts (matched by user.email == lead.email).
    Admins see all contracts in the tenant schema.

    Routes:
        GET /api/v1/investors/portal/          → list contracts
        GET /api/v1/investors/portal/my_summary/   → stats summary
        GET /api/v1/investors/portal/my_documents/ → contract PDF keys
    """
    permission_classes = [IsAuthenticated, IsTenantMember, IsInvestorOrAdmin]

    def _get_contracts(self, request):
        """Return Contract queryset filtered by role."""
        from apps.contracts.models import Contract
        from apps.memberships.models import TenantMembership

        qs = Contract.objects.select_related(
            'unit__floor__building__project',
            'lead',
            'vendor',
        ).prefetch_related('payments')

        # Investors only see their own contracts; admins see all.
        membership = TenantMembership.objects.filter(
            user=request.user, is_active=True,
        ).first()

        if membership and membership.role == TenantMembership.ROLE_INVESTIDOR:
            qs = qs.filter(lead__email=request.user.email)

        return qs

    def list(self, request):
        """List contracts visible to the authenticated user."""
        contracts = self._get_contracts(request)
        data = ContractSerializer(contracts, many=True).data
        return Response(data)

    @action(detail=False, methods=['get'], url_path='my_summary')
    def my_summary(self, request):
        """
        Aggregated dashboard summary:
        - units_by_status: {status: count}
        - total_invested_cve: sum of ACTIVE + COMPLETED contract values
        - upcoming_payments: payments due within 30 days (PENDING/OVERDUE)
        """
        from apps.contracts.models import Contract, Payment

        contracts = self._get_contracts(request)

        # Count units by contract status.
        units_by_status = {}
        for contract in contracts:
            units_by_status[contract.status] = units_by_status.get(contract.status, 0) + 1

        # Total invested = sum of active + completed contracts.
        invested = contracts.filter(
            status__in=[Contract.STATUS_ACTIVE, Contract.STATUS_COMPLETED],
        ).aggregate(total=Sum('total_price_cve'))['total'] or 0

        # Upcoming payments in the next 30 days.
        today = timezone.now().date()
        in_30_days = today + timedelta(days=30)
        upcoming = Payment.objects.filter(
            contract__in=contracts,
            due_date__range=[today, in_30_days],
            status__in=[Payment.STATUS_PENDING, Payment.STATUS_OVERDUE],
        ).select_related('contract__unit').order_by('due_date')

        return Response({
            'units_by_status': units_by_status,
            'total_invested_cve': str(invested),
            'upcoming_payments': PaymentSummarySerializer(upcoming, many=True).data,
        })

    @action(detail=False, methods=['get'], url_path='my_documents')
    def my_documents(self, request):
        """
        Return S3 keys (and contract metadata) for contracts that have a PDF.
        Frontend uses these to generate pre-signed download URLs.
        """
        contracts = self._get_contracts(request).exclude(pdf_s3_key='')
        data = [
            {
                'contract_number': c.contract_number,
                'unit_code': c.unit.code,
                'status': c.status,
                'pdf_s3_key': c.pdf_s3_key,
                'signed_at': c.signed_at.isoformat() if c.signed_at else None,
            }
            for c in contracts
        ]
        return Response(data)
