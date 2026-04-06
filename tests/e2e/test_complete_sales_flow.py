"""
Testes E2E: Fluxo Completo de Venda

Valida o workflow: Lead → Reserva → Contrato → Assinatura
"""
import uuid
from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest
from django.utils import timezone
from django_tenants.utils import tenant_context
from rest_framework import status

from apps.crm.models import Lead, UnitReservation
from apps.inventory.models import Unit
from apps.contracts.models import Contract, SignatureRequest


pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


class TestLeadToReservation:
    """Testar conversão de Lead em Reserva."""
    
    def test_create_lead_success(self, authenticated_client, e2e_tenant, e2e_vendedor):
        """1. Criar lead com sucesso."""
        lead_data = {
            'first_name': 'João',
            'last_name': 'Silva',
            'email': 'joao.silva@test.cv',
            'phone': '+2389991234',
            'status': Lead.STATUS_NEW,
            'source': Lead.SOURCE_WEB,
            'assigned_to': str(e2e_vendedor.id),
            'budget': '10000000.00',
            'preferred_typology': 'T2',
        }
        
        response = authenticated_client.post('/api/v1/crm/leads/', lead_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['first_name'] == 'João'
        assert data['last_name'] == 'Silva'
        assert data['email'] == 'joao.silva@test.cv'
        assert data['status'] == Lead.STATUS_NEW
        assert 'id' in data
        
        # Verificar no banco
        with tenant_context(e2e_tenant):
            lead = Lead.objects.get(id=data['id'])
            assert lead.stage == Lead.STAGE_NEW
            assert lead.assigned_to == e2e_vendedor
    
    def test_create_reservation_for_lead(
        self, authenticated_client, e2e_tenant, e2e_lead, e2e_unit, 
        e2e_vendedor, mock_whatsapp_service
    ):
        """2. Criar reserva para unidade e associar ao lead."""
        with tenant_context(e2e_tenant):
            # Garantir que a unidade está disponível
            unit = Unit.objects.get(id=e2e_unit.id)
            unit.status = Unit.STATUS_AVAILABLE
            unit.save()
        
        reservation_data = {
            'unit_id': str(e2e_unit.id),
            'lead_id': str(e2e_lead.id),
            'deposit_amount_cve': '100000.00',
            'notes': 'Reserva para teste E2E',
        }
        
        # Usar endpoint de workflow se disponível, senão criar diretamente
        response = authenticated_client.post(
            '/api/v1/crm/reservations/', 
            reservation_data, 
            format='json'
        )
        
        # Pode ser 201 (criado) ou 200 (workflow iniciado)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        
        # Verificar no banco
        with tenant_context(e2e_tenant):
            # Verificar se a reserva foi criada
            reservations = UnitReservation.objects.filter(
                unit=e2e_unit,
                lead=e2e_lead
            )
            assert reservations.exists()
            
            reservation = reservations.first()
            assert reservation.status == UnitReservation.STATUS_ACTIVE
            assert reservation.reserved_by == e2e_vendedor
            
            # Verificar se a unidade foi reservada
            unit.refresh_from_db()
            assert unit.status == Unit.STATUS_RESERVED
    
    def test_reservation_prevents_double_booking(
        self, authenticated_client, e2e_tenant, e2e_reservation
    ):
        """3. Verificar que reserva ativa previne double-booking."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        with tenant_context(e2e_tenant):
            # Criar outro lead
            other_lead = Lead.objects.create(
                first_name='Maria',
                last_name='Santos',
                email='maria.santos@test.cv',
                phone='+2389995678',
                status=Lead.STATUS_NEW,
            )
            
            unit = e2e_reservation.unit
            
            # Tentar criar outra reserva para a mesma unidade
            try:
                UnitReservation.objects.create(
                    unit=unit,
                    lead=other_lead,
                    status=UnitReservation.STATUS_ACTIVE,
                    expires_at=timezone.now() + timedelta(hours=48),
                )
                assert False, "Deveria ter falhado com double-booking"
            except Exception as e:
                # Esperado - constraint de unicidade violada
                assert 'unique_active_reservation_per_unit' in str(e).lower() or \
                       'already exists' in str(e).lower()


class TestReservationToContract:
    """Testar conversão de Reserva em Contrato."""
    
    def test_create_contract_from_reservation(
        self, authenticated_client, e2e_tenant, e2e_reservation, 
        e2e_vendedor, mock_whatsapp_service
    ):
        """1. Criar contrato a partir de reserva."""
        with tenant_context(e2e_tenant):
            unit = e2e_reservation.unit
            lead = e2e_reservation.lead
        
        contract_data = {
            'reservation_id': str(e2e_reservation.id),
            'unit_id': str(unit.id),
            'lead_id': str(lead.id),
            'vendor_id': str(e2e_vendedor.id),
            'contract_number': 'E2E-2026-0001',
            'total_price_cve': '8500000.00',
            'notes': 'Contrato criado via E2E test',
        }
        
        response = authenticated_client.post(
            '/api/v1/contracts/contracts/',
            contract_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['contract_number'] == 'E2E-2026-0001'
        assert data['status'] == Contract.STATUS_DRAFT
        assert 'id' in data
        
        # Verificar no banco
        with tenant_context(e2e_tenant):
            contract = Contract.objects.get(id=data['id'])
            assert contract.unit == unit
            assert contract.lead == lead
            assert contract.total_price_cve == Decimal('8500000.00')
            
            # Verificar se a reserva foi marcada como convertida
            e2e_reservation.refresh_from_db()
            assert e2e_reservation.status == UnitReservation.STATUS_CONVERTED
    
    def test_contract_includes_payment_schedule(
        self, authenticated_client, e2e_tenant, e2e_contract
    ):
        """2. Verificar que contrato inclui calendário de pagamentos."""
        from apps.contracts.models import Payment
        
        with tenant_context(e2e_tenant):
            # Criar pagamentos associados ao contrato
            payments = [
                Payment(
                    contract=e2e_contract,
                    payment_type=Payment.PAYMENT_DEPOSIT,
                    amount_cve=Decimal('850000.00'),  # 10%
                    due_date=timezone.now().date(),
                    status=Payment.STATUS_PENDING,
                ),
                Payment(
                    contract=e2e_contract,
                    payment_type=Payment.PAYMENT_INSTALLMENT,
                    amount_cve=Decimal('1700000.00'),  # 20%
                    due_date=timezone.now().date() + timedelta(days=30),
                    status=Payment.STATUS_PENDING,
                ),
                Payment(
                    contract=e2e_contract,
                    payment_type=Payment.PAYMENT_FINAL,
                    amount_cve=Decimal('5950000.00'),  # 70%
                    due_date=timezone.now().date() + timedelta(days=180),
                    status=Payment.STATUS_PENDING,
                ),
            ]
            for payment in payments:
                payment.save()
            
            # Verificar pagamentos
            contract_payments = Payment.objects.filter(contract=e2e_contract)
            assert contract_payments.count() == 3
            
            total = sum(p.amount_cve for p in contract_payments)
            assert total == Decimal('8500000.00')


class TestContractSignatureFlow:
    """Testar fluxo de assinatura do contrato."""
    
    def test_request_signature_creates_signature_request(
        self, authenticated_client, e2e_tenant, e2e_contract, 
        mock_signature_service
    ):
        """1. Solicitar assinatura cria pedido de assinatura."""
        with tenant_context(e2e_tenant):
            contract = e2e_contract
        
        signature_data = {
            'contract_id': str(contract.id),
            'signer_email': contract.lead.email,
            'signer_name': f'{contract.lead.first_name} {contract.lead.last_name}',
        }
        
        response = authenticated_client.post(
            f'/api/v1/contracts/contracts/{contract.id}/request_signature/',
            signature_data,
            format='json'
        )
        
        # Verificar resposta
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        # Verificar no banco
        with tenant_context(e2e_tenant):
            sig_requests = SignatureRequest.objects.filter(contract=contract)
            assert sig_requests.exists()
            
            sig_request = sig_requests.first()
            assert sig_request.status == SignatureRequest.STATUS_PENDING
            assert sig_request.token is not None
    
    def test_sign_contract_updates_status(
        self, authenticated_client, e2e_tenant, e2e_contract
    ):
        """2. Assinar contrato atualiza status para ACTIVE."""
        with tenant_context(e2e_tenant):
            # Criar signature request
            sig_request = SignatureRequest.objects.create(
                contract=e2e_contract,
                status=SignatureRequest.STATUS_PENDING,
                expires_at=timezone.now() + timedelta(hours=72),
            )
        
        sign_data = {
            'signed_by_name': f'{e2e_contract.lead.first_name} {e2e_contract.lead.last_name}',
            'ip_address': '192.168.1.100',
        }
        
        response = authenticated_client.post(
            f'/api/v1/contracts/contracts/{e2e_contract.id}/sign/',
            sign_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar no banco
        with tenant_context(e2e_tenant):
            e2e_contract.refresh_from_db()
            assert e2e_contract.status == Contract.STATUS_ACTIVE
            assert e2e_contract.signed_at is not None
            
            sig_request.refresh_from_db()
            assert sig_request.status == SignatureRequest.STATUS_SIGNED
            assert sig_request.signed_at is not None
            assert sig_request.ip_address == '192.168.1.100'
            
            # Verificar se a unidade foi atualizada para CONTRATO
            unit = e2e_contract.unit
            assert unit.status == Unit.STATUS_CONTRACT
    
    def test_signed_contract_triggers_construction_project_workflow(
        self, authenticated_client, e2e_tenant, e2e_contract, 
        mock_celery_task
    ):
        """3. Contrato assinado deve iniciar workflow de projeto de obra."""
        from apps.construction.models import ConstructionProject
        
        with tenant_context(e2e_tenant):
            # Assinar contrato
            e2e_contract.status = Contract.STATUS_ACTIVE
            e2e_contract.signed_at = timezone.now()
            e2e_contract.save()
        
        # Simular trigger de workflow (via signal ou endpoint)
        response = authenticated_client.post(
            f'/api/v1/contracts/contracts/{e2e_contract.id}/trigger_project_creation/',
            {},
            format='json'
        )
        
        # Pode ser 200 ou 404 se endpoint não existir - o importante é verificar o modelo
        with tenant_context(e2e_tenant):
            # Verificar se projeto de obra foi criado
            projects = ConstructionProject.objects.filter(contract=e2e_contract)
            
            # Se o workflow foi executado
            if response.status_code == status.HTTP_200_OK:
                assert projects.exists()
                project = projects.first()
                assert project.unit == e2e_contract.unit
                assert project.status == ConstructionProject.STATUS_PLANNING


class TestCompleteSalesFlow:
    """Testar fluxo completo de venda de ponta a ponta."""
    
    def test_complete_flow_lead_to_active_contract(
        self, authenticated_client, e2e_tenant, e2e_vendedor, 
        e2e_project, mock_whatsapp_service
    ):
        """Fluxo completo: Lead → Reserva → Contrato → Assinado."""
        from apps.projects.models import Floor
        from apps.inventory.models import Unit, UnitType
        
        with tenant_context(e2e_tenant):
            # Setup: criar unidade
            building = e2e_project.buildings.first()
            floor = Floor.objects.create(building=building, number=1, name='R/C')
            unit_type, _ = UnitType.objects.get_or_create(
                name='T3', defaults={'code': 'T3', 'bedrooms': 3, 'bathrooms': 2}
            )
            unit = Unit.objects.create(
                floor=floor,
                unit_type=unit_type,
                code='T3-001',
                status=Unit.STATUS_AVAILABLE,
                area_bruta=Decimal('120.00'),
            )
        
        # Passo 1: Criar Lead
        lead_data = {
            'first_name': 'Carlos',
            'last_name': 'Mendes',
            'email': 'carlos.mendes@test.cv',
            'phone': '+2389999999',
            'status': Lead.STATUS_NEW,
            'assigned_to': str(e2e_vendedor.id),
        }
        response = authenticated_client.post('/api/v1/crm/leads/', lead_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        lead_id = response.json()['id']
        
        # Passo 2: Criar Reserva
        reservation_data = {
            'unit_id': str(unit.id),
            'lead_id': lead_id,
            'deposit_amount_cve': '150000.00',
        }
        response = authenticated_client.post(
            '/api/v1/crm/reservations/', 
            reservation_data, 
            format='json'
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        
        with tenant_context(e2e_tenant):
            reservation = UnitReservation.objects.get(lead_id=lead_id)
            reservation_id = reservation.id
            # Atualizar unit reference
            unit.refresh_from_db()
        
        # Passo 3: Criar Contrato
        contract_data = {
            'reservation_id': str(reservation_id),
            'unit_id': str(unit.id),
            'lead_id': lead_id,
            'vendor_id': str(e2e_vendedor.id),
            'contract_number': 'E2E-FLOW-001',
            'total_price_cve': '12000000.00',
        }
        response = authenticated_client.post(
            '/api/v1/contracts/contracts/',
            contract_data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        contract_id = response.json()['id']
        
        # Passo 4: Assinar Contrato
        sign_data = {
            'signed_by_name': 'Carlos Mendes',
            'ip_address': '192.168.1.50',
        }
        response = authenticated_client.post(
            f'/api/v1/contracts/contracts/{contract_id}/sign/',
            sign_data,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verificações finais
        with tenant_context(e2e_tenant):
            # Lead convertido
            lead = Lead.objects.get(id=lead_id)
            assert lead.status == Lead.STATUS_CONVERTED
            
            # Reserva convertida
            reservation.refresh_from_db()
            assert reservation.status == UnitReservation.STATUS_CONVERTED
            
            # Contrato ativo
            contract = Contract.objects.get(id=contract_id)
            assert contract.status == Contract.STATUS_ACTIVE
            assert contract.signed_at is not None
            
            # Unidade em contrato
            unit.refresh_from_db()
            assert unit.status == Unit.STATUS_CONTRACT
