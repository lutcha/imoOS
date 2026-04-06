"""
Tests for Sales Workflow — Lead → Reserva → Contrato.
"""
from decimal import Decimal
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.workflows.services.sales_workflow import SalesWorkflow
from apps.crm.models import Lead, UnitReservation
from apps.contracts.models import Contract, SignatureRequest
from apps.inventory.models import Unit


@pytest.mark.django_db
def test_convert_lead_to_reservation_success(tenant_context, lead_factory, unit_factory, user_factory):
    """Test successful lead to reservation conversion."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        user = user_factory()
        lead = lead_factory(status=Lead.STATUS_QUALIFIED)
        unit = unit_factory(status=Unit.STATUS_AVAILABLE)
        
        result = SalesWorkflow.convert_lead_to_reservation(
            lead_id=str(lead.id),
            unit_id=str(unit.id),
            user=user,
            deposit_cve=Decimal('50000.00')
        )
        
        assert result['success'] is True
        assert 'reservation_id' in result
        assert result['unit_code'] == unit.code
        
        # Verify reservation created
        reservation = UnitReservation.objects.get(id=result['reservation_id'])
        assert reservation.lead == lead
        assert reservation.unit == unit
        assert reservation.status == UnitReservation.STATUS_ACTIVE
        
        # Verify unit status changed
        unit.refresh_from_db()
        assert unit.status == Unit.STATUS_RESERVED
        
        # Verify lead status changed
        lead.refresh_from_db()
        assert lead.status == Lead.STATUS_CONVERTED


@pytest.mark.django_db
def test_convert_lead_to_reservation_unit_not_available(tenant_context, lead_factory, unit_factory, user_factory):
    """Test reservation fails when unit is not available."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        user = user_factory()
        lead = lead_factory()
        unit = unit_factory(status=Unit.STATUS_RESERVED)
        
        result = SalesWorkflow.convert_lead_to_reservation(
            lead_id=str(lead.id),
            unit_id=str(unit.id),
            user=user
        )
        
        assert result['success'] is False
        assert 'não está disponível' in result['error']


@pytest.mark.django_db
def test_reservation_to_contract_success(tenant_context, reservation_factory, unit_factory, user_factory):
    """Test converting reservation to contract."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        user = user_factory()
        unit = unit_factory(status=Unit.STATUS_RESERVED)
        reservation = reservation_factory(
            unit=unit,
            status=UnitReservation.STATUS_ACTIVE
        )
        
        result = SalesWorkflow.reservation_to_contract(
            reservation_id=str(reservation.id),
            user=user
        )
        
        assert result['success'] is True
        assert 'contract_id' in result
        assert 'contract_number' in result
        
        # Verify contract created
        contract = Contract.objects.get(id=result['contract_id'])
        assert contract.reservation == reservation
        assert contract.status == Contract.STATUS_DRAFT
        
        # Verify reservation updated
        reservation.refresh_from_db()
        assert reservation.status == UnitReservation.STATUS_CONVERTED
        
        # Verify unit status changed
        unit.refresh_from_db()
        assert unit.status == Unit.STATUS_CONTRACT


@pytest.mark.django_db
def test_create_signature_request(tenant_context, contract_factory, user_factory):
    """Test creating signature request."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        contract = contract_factory(status=Contract.STATUS_DRAFT)
        
        result = SalesWorkflow.create_signature_request(
            contract_id=str(contract.id)
        )
        
        assert result['success'] is True
        assert 'signature_request_id' in result
        assert 'token' in result
        
        # Verify signature request created
        sig_request = SignatureRequest.objects.get(id=result['signature_request_id'])
        assert sig_request.contract == contract
        assert sig_request.status == SignatureRequest.STATUS_PENDING
        
        # Verify contract updated
        contract.refresh_from_db()
        assert contract.signature_request == sig_request


@pytest.mark.django_db
def test_mark_contract_signed(tenant_context, contract_factory, signature_request_factory):
    """Test marking contract as signed."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        contract = contract_factory(status=Contract.STATUS_DRAFT)
        sig_request = signature_request_factory(
            contract=contract,
            status=SignatureRequest.STATUS_PENDING
        )
        contract.signature_request = sig_request
        contract.save()
        
        result = SalesWorkflow.mark_contract_signed(
            contract_id=str(contract.id),
            signature_data={
                'ip_address': '192.168.1.1',
                'signed_by_name': 'João Silva'
            }
        )
        
        assert result['success'] is True
        
        # Verify contract updated
        contract.refresh_from_db()
        assert contract.status == Contract.STATUS_ACTIVE
        assert contract.signed_at is not None
        
        # Verify signature request updated
        sig_request.refresh_from_db()
        assert sig_request.status == SignatureRequest.STATUS_SIGNED


@pytest.mark.django_db
def test_contract_to_deed(tenant_context, contract_factory):
    """Test preparing deed for completed contract."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        contract = contract_factory(
            status=Contract.STATUS_ACTIVE,
            signed_at=timezone.now()
        )
        
        result = SalesWorkflow.contract_to_deed(
            contract_id=str(contract.id),
            deed_date='2026-12-31'
        )
        
        assert result['success'] is True
        assert result['deed_date'] == '2026-12-31'
        
        # Verify contract marked as completed
        contract.refresh_from_db()
        assert contract.status == Contract.STATUS_COMPLETED


@pytest.mark.django_db
def test_contract_to_deed_not_active(tenant_context, contract_factory):
    """Test deed preparation fails if contract not active."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        contract = contract_factory(status=Contract.STATUS_DRAFT)
        
        result = SalesWorkflow.contract_to_deed(
            contract_id=str(contract.id)
        )
        
        assert result['success'] is False
        assert 'deve estar activo' in result['error']
