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
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.tenants.permissions import IsTenantAdmin
from apps.users.permissions import IsTenantMember

from .filters import ContractFilter, PaymentFilter
from .models import Contract, Payment, ContractTemplate, PaymentPattern
from .serializers import (
    ContractCreateSerializer,
    ContractSerializer,
    PaymentMarkPaidSerializer,
    PaymentSerializer,
    GeneratePaymentPlanSerializer,
    ContractTemplateSerializer,
    PaymentPatternSerializer,
)
from .services import ContractAutomationService
from dateutil.relativedelta import relativedelta
from decimal import Decimal


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
            template_id=data.get('template_id'),
            payment_pattern_id=data.get('payment_pattern_id'),
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


    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTenantAdmin])
    def update_pdf(self, request, pk=None):
        """
        Força regeração do PDF do contrato.
        """
        contract = self.get_object()
        if not contract.template:
             return Response({'detail': 'Contrato não tem template associado.'}, status=400)
             
        from .tasks import generate_contract_pdf
        generate_contract_pdf.delay(
            tenant_schema=request.tenant.schema_name,
            contract_id=str(contract.id),
        )
        return Response({'detail': 'PDF em actualização.'})


    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTenantAdmin])
    def generate_payment_plan(self, request, pk=None):
        """
        Generate a payment plan for the contract based on provided percentages and installments.
        """
        contract = self.get_object()
        if contract.status != Contract.STATUS_DRAFT:
            return Response(
                {'detail': 'Apenas contratos em rascunho podem gerar planos de pagamento.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = GeneratePaymentPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        ContractAutomationService.generate_payments_from_params(
            contract,
            data['deposit_percentage'],
            data['final_percentage'],
            data['installments_count'],
            data['start_date']
        )

        return Response(PaymentSerializer(contract.payments.order_by('due_date'), many=True).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTenantAdmin])
    def apply_pattern(self, request, pk=None):
        """
        Apply a saved PaymentPattern to the contract.
        Body: {"pattern_id": "...", "start_date": "YYYY-MM-DD"}
        """
        contract = self.get_object()
        if contract.status != Contract.STATUS_DRAFT:
            return Response({'detail': 'Apenas rascunhos podem ser alterados.'}, status=400)

        pattern_id = request.data.get('pattern_id')
        start_date_str = request.data.get('start_date')

        if not pattern_id or not start_date_str:
            return Response({'detail': 'pattern_id e start_date são obrigatórios.'}, status=400)

        try:
            pattern = PaymentPattern.objects.get(id=pattern_id)
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except (PaymentPattern.DoesNotExist, ValueError):
            return Response({'detail': 'Padrão ou data inválida.'}, status=400)

        ContractAutomationService.apply_payment_pattern(contract, pattern, start_date)
        
        contract.payment_pattern = pattern
        contract.save(update_fields=['payment_pattern', 'updated_at'])

        return Response(PaymentSerializer(contract.payments.order_by('due_date'), many=True).data)


class ContractTemplateViewSet(viewsets.ModelViewSet):
    queryset = ContractTemplate.objects.all()
    serializer_class = ContractTemplateSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class PaymentPatternViewSet(viewsets.ModelViewSet):
    queryset = PaymentPattern.objects.all()
    serializer_class = PaymentPatternSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


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


class SignatureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gestão de pedidos de assinatura.
    Inclui acções públicas para o portal do cliente.
    """
    queryset = Contract.objects.none() # Not used for public actions
    
    def get_permissions(self):
        if self.action in ['public_detail', 'public_sign']:
            return [AllowAny()]
        return [IsAuthenticated(), IsTenantAdmin()]

    @action(detail=False, methods=['get'])
    def public_detail(self, request):
        """
        Retorna detalhes do contrato para o portal de assinatura.
        Filtra por token UUID único.
        """
        from apps.contracts.models import SignatureRequest
        token = request.query_params.get('token')
        if not token:
            return Response({'detail': 'Token é obrigatório.'}, status=400)
            
        try:
            sr = SignatureRequest.objects.select_related('contract', 'contract__unit', 'contract__lead').get(token=token)
        except (SignatureRequest.DoesNotExist, ValueError):
            return Response({'detail': 'Pedido de assinatura não encontrado ou link inválido.'}, status=404)
            
        if sr.status != SignatureRequest.STATUS_PENDING:
            return Response({'detail': f'Este pedido já não está pendente (Estado: {sr.get_status_display()}).'}, status=400)
            
        if sr.is_expired:
             sr.status = SignatureRequest.STATUS_EXPIRED
             sr.save(update_fields=['status'])
             return Response({'detail': 'O link de assinatura expirou.'}, status=400)

        # Return a subset of contract info for the public portal
        return Response({
            'id': sr.id,
            'contract_number': sr.contract.contract_number,
            'lead_name': sr.contract.lead.full_name,
            'unit_code': sr.contract.unit.code,
            'total_price_cve': sr.contract.total_price_cve,
            'expires_at': sr.expires_at,
        })

    @action(detail=False, methods=['post'])
    def public_sign(self, request):
        """
        Regista a assinatura e activa o contrato.
        Recebe: token, full_name, signature_base64 (PNG data path).
        """
        from apps.contracts.models import SignatureRequest
        from apps.contracts.services import ContractAutomationService
        import base64
        from django.core.files.base import ContentFile

        token = request.data.get('token')
        full_name = request.data.get('full_name')
        signature_base64 = request.data.get('signature_base64') # data:image/png;base64,...

        if not all([token, full_name, signature_base64]):
            return Response({'detail': 'Todos os campos são obrigatórios.'}, status=400)

        try:
            sr = SignatureRequest.objects.get(token=token, status=SignatureRequest.STATUS_PENDING)
        except SignatureRequest.DoesNotExist:
            return Response({'detail': 'Pedido não encontrado ou já processado.'}, status=404)

        if sr.is_expired:
            return Response({'detail': 'O link expirou.'}, status=400)

        # Process signature image
        try:
            format, imgstr = signature_base64.split(';base64,') 
            ext = format.split('/')[-1] 
            data = ContentFile(base64.b64decode(imgstr), name=f"sig_{sr.id}.{ext}")
        except Exception:
            return Response({'detail': 'Formato de assinatura inválido.'}, status=400)

        # Update SignatureRequest
        sr.signed_at = timezone.now()
        sr.signed_by_name = full_name
        sr.status = SignatureRequest.STATUS_SIGNED
        sr.ip_address = request.META.get('REMOTE_ADDR')
        
        # In a real scenario, we would upload 'data' to S3 here.
        # For now, we'll mark it as signed and proceed to activate the contract.
        sr.save()

        # Activate the contract (logic reused from activate action)
        # However, it's better to use a dedicated service method.
        # For simplicity in this sprint, we just mark the contract as active.
        contract = sr.contract
        contract.status = Contract.STATUS_ACTIVE
        contract.signed_at = sr.signed_at
        contract.save()

        # Enqueue PDF generation
        from .tasks import generate_contract_pdf
        generate_contract_pdf.delay(
            tenant_schema=request.tenant.schema_name,
            contract_id=str(contract.id),
        )

        return Response({'detail': 'Contrato assinado e activado com sucesso!'})
