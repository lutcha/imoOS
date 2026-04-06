"""
Sales Workflow — Lead → Reserva → Contrato → Assinatura

Este módulo implementa o workflow completo de venda:
1. Lead qualificado reserva unidade
2. Reserva convertida em contrato CPV
3. Contrato enviado para assinatura digital
4. Após assinatura, preparação para escritura
"""
import logging
from decimal import Decimal
from datetime import timedelta
from typing import Optional

from django.db import transaction
from django.utils import timezone
from django.conf import settings

from apps.workflows.models import (
    WorkflowInstance, WorkflowStep, WorkflowLog,
    WorkflowDefinition
)

logger = logging.getLogger(__name__)


class SalesWorkflow:
    """
    Workflow completo de venda: Lead → Reserva → Contrato → Assinatura
    """
    
    @classmethod
    @transaction.atomic
    def convert_lead_to_reservation(
        cls,
        lead_id: str,
        unit_id: str,
        user=None,
        deposit_cve: Decimal = Decimal('0.00'),
        notes: str = '',
    ) -> dict:
        """
        Lead qualificado reserva unidade.
        
        Args:
            lead_id: UUID do lead
            unit_id: UUID da unidade
            user: User que está criando a reserva
            deposit_cve: Valor do sinal (opcional)
            notes: Notas adicionais
            
        Returns:
            dict com reservation_id, status e mensagem
        """
        from apps.crm.services import create_reservation
        from apps.crm.models import Lead
        from apps.inventory.models import Unit
        
        logger.info(f'Starting reservation workflow: lead={lead_id}, unit={unit_id}')
        
        try:
            # 1. Verificar se lead existe e está qualificado
            lead = Lead.objects.get(id=lead_id)
            if lead.status not in [Lead.STATUS_QUALIFIED, Lead.STATUS_NEW, Lead.STATUS_CONTACTED]:
                return {
                    'success': False,
                    'error': f'Lead não está em estado válido para reserva: {lead.status}'
                }
            
            # 2. Verificar disponibilidade da unidade
            unit = Unit.objects.get(id=unit_id)
            if unit.status != Unit.STATUS_AVAILABLE:
                return {
                    'success': False,
                    'error': f'Unidade {unit.code} não está disponível (estado: {unit.status})'
                }
            
            # 3. Criar reserva (usa SELECT FOR UPDATE via serviço existente)
            reservation = create_reservation(
                unit_id=unit_id,
                lead_id=lead_id,
                user=user,
                notes=notes,
                deposit_cve=deposit_cve,
            )
            
            # 4. Atualizar lead
            lead.status = Lead.STATUS_CONVERTED
            lead.interested_unit = unit
            lead.save(update_fields=['status', 'interested_unit', 'updated_at'])
            
            # 5. Criar workflow instance para tracking
            try:
                workflow_def = WorkflowDefinition.objects.get(
                    workflow_type=WorkflowDefinition.TYPE_SALES,
                    is_active=True
                )
                instance = WorkflowInstance.objects.create(
                    workflow=workflow_def,
                    status=WorkflowInstance.STATUS_COMPLETED,
                    context={
                        'lead_id': str(lead_id),
                        'unit_id': str(unit_id),
                        'reservation_id': str(reservation.id),
                        'step': 'reservation_created'
                    },
                    trigger_model='Lead',
                    trigger_object_id=str(lead_id),
                    current_step=1,
                    total_steps=3,
                    completed_at=timezone.now()
                )
            except WorkflowDefinition.DoesNotExist:
                instance = None
            
            # 6. Enviar notificação WhatsApp (async)
            from apps.workflows.tasks import send_workflow_notification
            send_workflow_notification.delay(
                notification_type='reservation_created',
                lead_id=str(lead_id),
                reservation_id=str(reservation.id),
                unit_code=unit.code
            )
            
            return {
                'success': True,
                'reservation_id': str(reservation.id),
                'unit_code': unit.code,
                'lead_name': lead.full_name,
                'expires_at': reservation.expires_at.isoformat(),
                'workflow_instance_id': str(instance.id) if instance else None,
                'message': f'Reserva criada com sucesso. Expira em {reservation.expires_at.strftime("%d/%m/%Y %H:%M")}'
            }
            
        except Exception as e:
            logger.error(f'Error creating reservation: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    @transaction.atomic
    def reservation_to_contract(
        cls,
        reservation_id: str,
        user=None,
    ) -> dict:
        """
        Converter reserva em contrato.
        
        Args:
            reservation_id: UUID da reserva
            user: User que está criando o contrato
            
        Returns:
            dict com contract_id e dados do contrato
        """
        from apps.crm.models import UnitReservation
        from apps.contracts.models import Contract, SignatureRequest
        from apps.inventory.models import Unit
        
        logger.info(f'Converting reservation to contract: reservation={reservation_id}')
        
        try:
            # 1. Buscar reserva
            reservation = UnitReservation.objects.select_related(
                'lead', 'unit', 'unit__floor', 'unit__floor__building',
                'unit__floor__building__project'
            ).get(id=reservation_id)
            
            if reservation.status != UnitReservation.STATUS_ACTIVE:
                return {
                    'success': False,
                    'error': f'Reserva não está activa (estado: {reservation.status})'
                }
            
            # 2. Gerar número de contrato
            contract_number = cls._generate_contract_number(reservation)
            
            # 3. Determinar preço
            unit = reservation.unit
            try:
                pricing = unit.pricing
                total_price = pricing.final_price_cve
            except AttributeError:
                total_price = Decimal('0.00')
            
            # 4. Criar contrato
            contract = Contract.objects.create(
                reservation=reservation,
                unit=unit,
                lead=reservation.lead,
                vendor=user,
                status=Contract.STATUS_DRAFT,
                contract_number=contract_number,
                total_price_cve=total_price,
                notes=f'Criado a partir da reserva #{reservation.id}'
            )
            
            # 5. Atualizar status da unidade
            unit.status = Unit.STATUS_CONTRACT
            unit.save(update_fields=['status', 'updated_at'])
            
            # 6. Atualizar reserva
            reservation.status = UnitReservation.STATUS_CONVERTED
            reservation.save(update_fields=['status', 'updated_at'])
            
            return {
                'success': True,
                'contract_id': str(contract.id),
                'contract_number': contract_number,
                'total_price_cve': str(total_price),
                'lead_name': reservation.lead.full_name,
                'unit_code': unit.code,
                'message': 'Contrato criado com sucesso. Aguardando assinatura.'
            }
            
        except Exception as e:
            logger.error(f'Error converting reservation to contract: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def create_signature_request(
        cls,
        contract_id: str,
        user=None,
    ) -> dict:
        """
        Criar pedido de assinatura digital para um contrato.
        
        Args:
            contract_id: UUID do contrato
            user: User que está criando o pedido
            
        Returns:
            dict com signature_request_id e token
        """
        from apps.contracts.models import Contract, SignatureRequest
        
        logger.info(f'Creating signature request: contract={contract_id}')
        
        try:
            contract = Contract.objects.select_related('lead').get(id=contract_id)
            
            if contract.status != Contract.STATUS_DRAFT:
                return {
                    'success': False,
                    'error': f'Contrato deve estar em rascunho (estado actual: {contract.status})'
                }
            
            # Criar pedido de assinatura
            signature_request = SignatureRequest.objects.create(
                contract=contract,
                expires_at=timezone.now() + timedelta(hours=72),
                status=SignatureRequest.STATUS_PENDING
            )
            
            # Linkar ao contrato
            contract.signature_request = signature_request
            contract.save(update_fields=['signature_request'])
            
            # Enviar notificação WhatsApp
            from apps.workflows.tasks import send_workflow_notification
            send_workflow_notification.delay(
                notification_type='signature_requested',
                lead_id=str(contract.lead.id),
                contract_id=str(contract.id),
                signature_token=str(signature_request.token)
            )
            
            return {
                'success': True,
                'signature_request_id': str(signature_request.id),
                'token': str(signature_request.token),
                'expires_at': signature_request.expires_at.isoformat(),
                'message': 'Pedido de assinatura criado com sucesso'
            }
            
        except Exception as e:
            logger.error(f'Error creating signature request: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def mark_contract_signed(
        cls,
        contract_id: str,
        signature_data: dict = None,
    ) -> dict:
        """
        Marcar contrato como assinado.
        
        Args:
            contract_id: UUID do contrato
            signature_data: Dados da assinatura (IP, nome, etc.)
            
        Returns:
            dict com status atualizado
        """
        from apps.contracts.models import Contract, SignatureRequest
        from apps.inventory.models import Unit
        
        logger.info(f'Marking contract as signed: contract={contract_id}')
        
        try:
            contract = Contract.objects.select_related('lead', 'unit').get(id=contract_id)
            
            contract.status = Contract.STATUS_ACTIVE
            contract.signed_at = timezone.now()
            contract.save(update_fields=['status', 'signed_at'])
            
            # Atualizar unidade para SOLD
            unit = contract.unit
            unit.status = Unit.STATUS_SOLD
            unit.save(update_fields=['status', 'updated_at'])
            
            # Atualizar signature request
            if contract.signature_request:
                sig = contract.signature_request
                sig.status = SignatureRequest.STATUS_SIGNED
                sig.signed_at = timezone.now()
                if signature_data:
                    sig.ip_address = signature_data.get('ip_address')
                    sig.signed_by_name = signature_data.get('signed_by_name')
                sig.save()
            
            # Criar plano de pagamento automaticamente
            from apps.payments.models import PaymentPlan
            payment_plan, created = PaymentPlan.objects.get_or_create(
                contract=contract,
                defaults={
                    'total_cve': contract.total_price_cve,
                    'plan_type': PaymentPlan.TYPE_STANDARD
                }
            )
            
            if created:
                payment_plan.generate_standard()
            
            # Notificar cliente
            from apps.workflows.tasks import send_workflow_notification
            send_workflow_notification.delay(
                notification_type='contract_signed',
                lead_id=str(contract.lead.id),
                contract_id=str(contract.id),
                contract_number=contract.contract_number
            )
            
            return {
                'success': True,
                'contract_id': str(contract.id),
                'contract_number': contract.contract_number,
                'signed_at': contract.signed_at.isoformat(),
                'payment_plan_created': created,
                'message': 'Contrato assinado com sucesso'
            }
            
        except Exception as e:
            logger.error(f'Error marking contract as signed: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def contract_to_deed(
        cls,
        contract_id: str,
        deed_date: Optional[str] = None,
        notes: str = '',
    ) -> dict:
        """
        Preparar escritura após contrato assinado.
        
        Args:
            contract_id: UUID do contrato
            deed_date: Data prevista para escritura (ISO format)
            notes: Notas adicionais
            
        Returns:
            dict com status atualizado
        """
        from apps.contracts.models import Contract
        
        logger.info(f'Preparing deed: contract={contract_id}')
        
        try:
            contract = Contract.objects.get(id=contract_id)
            
            if contract.status != Contract.STATUS_ACTIVE:
                return {
                    'success': False,
                    'error': 'Contrato deve estar activo e assinado'
                }
            
            # Verificar pagamentos
            payments = contract.payments.all()
            paid_amount = sum(p.amount_cve for p in payments if p.status == 'PAID')
            total_amount = contract.total_price_cve
            
            # Marcar contrato como completado
            contract.status = Contract.STATUS_COMPLETED
            contract.save(update_fields=['status', 'updated_at'])
            
            result = {
                'success': True,
                'contract_id': str(contract.id),
                'contract_number': contract.contract_number,
                'paid_amount': str(paid_amount),
                'total_amount': str(total_amount),
                'payment_percentage': float(paid_amount / total_amount * 100) if total_amount else 0,
                'message': 'Contrato concluído. Pronto para escritura.'
            }
            
            if deed_date:
                result['deed_date'] = deed_date
            
            return result
            
        except Exception as e:
            logger.error(f'Error preparing deed: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _generate_contract_number(reservation) -> str:
        """Gerar número único de contrato."""
        from datetime import datetime
        year = datetime.now().year
        
        # Buscar último número do ano
        from apps.contracts.models import Contract
        last_contract = Contract.objects.filter(
            contract_number__startswith=f'IMO-{year}'
        ).order_by('-contract_number').first()
        
        if last_contract:
            # Extrair número e incrementar
            try:
                last_num = int(last_contract.contract_number.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1
        
        return f'IMO-{year}-{new_num:04d}'
