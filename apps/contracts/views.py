"""
Contract and Payment ViewSets for ImoOS.

Write operations on contracts (create, activate, cancel) require IsTenantAdmin.
Read operations and payment management are open to any IsTenantMember.
All tenant isolation is enforced at the schema level by django-tenants middleware.
"""
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tenants.permissions import IsTenantAdmin
from apps.users.permissions import IsTenantMember

from .filters import ContractFilter, PaymentFilter
from .models import Contract, Payment
from .serializers import (
    ContractCreateSerializer,
    ContractSerializer,
    PaymentMarkPaidSerializer,
    PaymentSerializer,
)


class ContractViewSet(viewsets.ModelViewSet):
    """
    CRUD for contracts.
    - list / retrieve: IsTenantMember
    - create / update / destroy + custom actions: IsTenantAdmin
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ContractFilter
    search_fields = ['contract_number', 'unit__code', 'lead__first_name', 'lead__last_name']
    ordering_fields = ['created_at', 'signed_at', 'total_price_cve']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsTenantMember()]
        return [IsAuthenticated(), IsTenantAdmin()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ContractCreateSerializer
        return ContractSerializer

    def get_queryset(self):
        return (
            Contract.objects
            .select_related('unit', 'lead', 'vendor', 'reservation')
            .prefetch_related('payments')
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        """
        Auto-generate contract_number = ImoOS-{year}-{count:04d}.
        Set vendor to the authenticated user making the request.
        The ContractCreateSerializer is a plain Serializer, so we resolve
        foreign-key objects here before calling Contract.objects.create().
        """
        from apps.crm.models import Lead, UnitReservation
        from apps.inventory.models import Unit

        data = serializer.validated_data
        year = timezone.now().year
        count = Contract.objects.filter(created_at__year=year).count() + 1
        contract_number = f'ImoOS-{year}-{count:04d}'

        Contract.objects.create(
            reservation_id=data['reservation_id'],
            unit_id=data['unit_id'],
            lead_id=data['lead_id'],
            vendor=self.request.user,
            total_price_cve=data['total_price_cve'],
            notes=data.get('notes', ''),
            contract_number=contract_number,
            status=Contract.STATUS_DRAFT,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Fetch the newly created contract for the response
        year = timezone.now().year
        contract = (
            Contract.objects
            .select_related('unit', 'lead', 'vendor', 'reservation')
            .prefetch_related('payments')
            .filter(vendor=request.user, created_at__year=year)
            .order_by('-created_at')
            .first()
        )
        return Response(
            ContractSerializer(contract, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Transition a DRAFT contract to ACTIVE.

        Steps (all inside a single atomic transaction):
        1. Validate the contract is in DRAFT status.
        2. Call convert_reservation() — marks the reservation CONVERTED and
           sets unit.status = CONTRACT.
        3. Set contract.status = ACTIVE and contract.signed_at = now().
        4. Enqueue generate_contract_pdf Celery task.
        5. Attempt to advance the lead stage to 'won' (best-effort).
        """
        from apps.crm.services import InvalidStageTransitionError, advance_lead_stage, convert_reservation

        contract = self.get_object()

        if contract.status != Contract.STATUS_DRAFT:
            return Response(
                {'detail': 'Apenas contratos em rascunho podem ser activados.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            convert_reservation(str(contract.reservation_id), request.user)
            contract.status = Contract.STATUS_ACTIVE
            contract.signed_at = timezone.now()
            contract._change_reason = f'Activado por {request.user.email}'
            contract.save(update_fields=['status', 'signed_at', 'updated_at'])

        # Enqueue PDF generation outside the transaction so a task-broker
        # failure does not roll back the contract state change.
        try:
            from .tasks import generate_contract_pdf
            generate_contract_pdf.delay(
                tenant_schema=request.tenant.schema_name,
                contract_id=str(contract.id),
            )
        except Exception:
            # PDF generation is async and non-critical at this point;
            # the contract is already ACTIVE. The task can be retried manually.
            pass

        # Advance lead stage to 'won' — silently skip invalid transitions.
        try:
            advance_lead_stage(str(contract.lead_id), 'won', request.user)
        except (InvalidStageTransitionError, Exception):
            pass

        contract.refresh_from_db()
        return Response(
            ContractSerializer(contract, context={'request': request}).data
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an ACTIVE contract.

        The reservation was already CONVERTED by activate(), so we must not
        call cancel_reservation() here (it only operates on ACTIVE reservations).
        Instead we release the unit directly with SELECT FOR UPDATE and set
        its status back to AVAILABLE.
        """
        from apps.inventory.models import Unit

        contract = self.get_object()

        if contract.status != Contract.STATUS_ACTIVE:
            return Response(
                {'detail': 'Apenas contratos activos podem ser cancelados.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Re-lock the unit row to prevent concurrent status drift.
            unit = Unit.objects.select_for_update().get(id=contract.unit_id)
            if unit.status == Unit.STATUS_CONTRACT:
                unit.status = Unit.STATUS_AVAILABLE
                unit._change_reason = f'Contrato #{contract.contract_number} cancelado'
                unit.save(update_fields=['status', 'updated_at'])

            contract.status = Contract.STATUS_CANCELLED
            contract._change_reason = f'Cancelado por {request.user.email}'
            contract.save(update_fields=['status', 'updated_at'])

        contract.refresh_from_db()
        return Response(
            ContractSerializer(contract, context={'request': request}).data
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTenantAdmin])
    def request_signature(self, request, pk=None):
        """
        Cria SignatureRequest e envia link ao comprador via WhatsApp.
        Idempotente: cancela request anterior se existir.
        """
        from apps.contracts.models import SignatureRequest
        from apps.contracts.tasks import send_signature_request_whatsapp
        from django.conf import settings
        from django.db import connection

        contract = self.get_object()
        if contract.status != Contract.STATUS_DRAFT:
            return Response({'detail': 'Apenas contratos em rascunho podem ser enviados para assinatura.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Cancelar requests anteriores pendentes
        contract.signature_requests.filter(
            status=SignatureRequest.STATUS_PENDING,
        ).update(status=SignatureRequest.STATUS_CANCELLED)

        sr = SignatureRequest.objects.create(contract=contract)
        
        public_base_url = getattr(settings, 'PUBLIC_BASE_URL', 'http://localhost:3000')
        sign_url = f"{public_base_url}/sign/{sr.token}/"

        # Enviar WhatsApp ao lead
        send_signature_request_whatsapp.delay(
            tenant_schema=connection.schema_name,
            signature_request_id=str(sr.id),
            sign_url=sign_url,
        )
        return Response({'signature_url': sign_url, 'expires_at': sr.expires_at})


class PaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD for payments linked to a contract.
    All authenticated tenant members can read and manage payments.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['due_date', 'amount_cve', 'status']

    def get_queryset(self):
        return (
            Payment.objects
            .select_related('contract')
            .order_by('due_date')
        )

    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        """
        Mark a pending payment as PAID.
        Body: {"paid_date": "YYYY-MM-DD" (optional, defaults to today), "reference": "..."}
        """
        payment = self.get_object()

        if payment.status == Payment.STATUS_PAID:
            return Response(
                {'detail': 'Este pagamento já foi registado como pago.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PaymentMarkPaidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        payment.paid_date = d['paid_date']
        payment.status = Payment.STATUS_PAID
        if d.get('reference'):
            payment.reference = d['reference']
        payment.save(update_fields=['paid_date', 'status', 'reference', 'updated_at'])

        return Response(PaymentSerializer(payment).data)
