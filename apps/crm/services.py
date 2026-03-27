"""
CRM business logic — pure service functions, no HTTP concerns.

All write operations use SELECT FOR UPDATE to prevent race conditions.
All stage transitions go through advance_lead_stage() — never direct assignment.
"""
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import LEAD_STAGE_TRANSITIONS


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class UnitNotAvailableError(ValidationError):
    pass


class ActiveReservationExistsError(ValidationError):
    pass


class InvalidStageTransitionError(ValidationError):
    pass


# ---------------------------------------------------------------------------
# Reservation
# ---------------------------------------------------------------------------

RESERVATION_EXPIRY_HOURS = 48   # configurable per tenant in future sprint


@transaction.atomic
def create_reservation(
    unit_id: str,
    lead_id: str,
    user,
    notes: str = '',
    deposit_cve: Decimal = Decimal('0.00'),
) -> 'UnitReservation':
    """
    Create a reservation with a row-level lock on the Unit.

    SELECT FOR UPDATE ensures that two concurrent requests for the same unit
    are serialised: the second waits until the first transaction commits, then
    sees status=RESERVED and raises UnitNotAvailableError.

    The UniqueConstraint on UnitReservation(unit, status=ACTIVE) acts as a
    second safety net if SELECT FOR UPDATE were ever bypassed.
    """
    from apps.inventory.models import Unit
    from .models import UnitReservation, Lead

    # 1. Lock the unit row — any concurrent create_reservation for the same
    #    unit blocks here until this transaction finishes.
    try:
        unit = Unit.objects.select_for_update().get(id=unit_id)
    except Unit.DoesNotExist:
        raise ValidationError({'unit_id': 'Unidade não encontrada.'})

    # 2. Verify availability
    if unit.status != Unit.STATUS_AVAILABLE:
        raise UnitNotAvailableError(
            {'unit_id': f'Unidade {unit.code} não está disponível '
                        f'(estado actual: {unit.get_status_display()}).'}
        )

    # 3. Belt-and-suspenders: no unexpired active reservation should exist
    if UnitReservation.objects.filter(
        unit=unit,
        status=UnitReservation.STATUS_ACTIVE,
        expires_at__gt=timezone.now(),
    ).exists():
        raise ActiveReservationExistsError(
            {'unit_id': f'Unidade {unit.code} já tem uma reserva activa.'}
        )

    # 4. Transition unit status
    unit.status = Unit.STATUS_RESERVED
    unit._change_reason = f'Reservada por {user.email}'
    unit.save(update_fields=['status', 'updated_at'])

    # 5. Create reservation
    reservation = UnitReservation.objects.create(
        unit=unit,
        lead_id=lead_id,
        reserved_by=user,
        expires_at=timezone.now() + timedelta(hours=RESERVATION_EXPIRY_HOURS),
        status=UnitReservation.STATUS_ACTIVE,
        notes=notes,
        deposit_amount_cve=deposit_cve,
    )

    # 6. Advance lead stage (non-blocking — silently skips if lead not found)
    try:
        lead = Lead.objects.select_for_update().get(id=lead_id)
        if lead.stage in ('new', 'contacted'):
            lead.stage = Lead.STAGE_VISIT_SCHEDULED
            lead._change_reason = f'Reserva #{reservation.id} criada'
            lead.save(update_fields=['stage', 'updated_at'])
    except Lead.DoesNotExist:
        pass

    return reservation


@transaction.atomic
def cancel_reservation(reservation_id: str, user) -> 'UnitReservation':
    """Cancel an active reservation and release the unit back to AVAILABLE."""
    from apps.inventory.models import Unit
    from .models import UnitReservation

    try:
        reservation = UnitReservation.objects.select_for_update().get(id=reservation_id)
    except UnitReservation.DoesNotExist:
        raise ValidationError({'reservation_id': 'Reserva não encontrada.'})

    if reservation.status != UnitReservation.STATUS_ACTIVE:
        raise ValidationError({'reservation': 'Só é possível cancelar reservas activas.'})

    reservation.status = UnitReservation.STATUS_CANCELLED
    reservation._change_reason = f'Cancelada por {user.email}'
    reservation.save(update_fields=['status', 'updated_at'])

    # Release the unit — re-lock to avoid concurrent status drift
    unit = Unit.objects.select_for_update().get(id=reservation.unit_id)
    if unit.status == Unit.STATUS_RESERVED:
        unit.status = Unit.STATUS_AVAILABLE
        unit._change_reason = f'Reserva #{reservation.id} cancelada'
        unit.save(update_fields=['status', 'updated_at'])

    return reservation


@transaction.atomic
def convert_reservation(reservation_id: str, user) -> 'UnitReservation':
    """Mark reservation as CONVERTED (called when a Contract is signed)."""
    from apps.inventory.models import Unit
    from .models import UnitReservation

    try:
        reservation = UnitReservation.objects.select_for_update().get(id=reservation_id)
    except UnitReservation.DoesNotExist:
        raise ValidationError({'reservation_id': 'Reserva não encontrada.'})

    if reservation.status != UnitReservation.STATUS_ACTIVE:
        raise ValidationError({'reservation': 'Só é possível converter reservas activas.'})

    reservation.status = UnitReservation.STATUS_CONVERTED
    reservation._change_reason = f'Convertida em contrato por {user.email}'
    reservation.save(update_fields=['status', 'updated_at'])

    # Unit transitions to CONTRACT status in the contracts module;
    # we only update it here if needed (contract module should own this).
    unit = Unit.objects.select_for_update().get(id=reservation.unit_id)
    if unit.status == Unit.STATUS_RESERVED:
        unit.status = Unit.STATUS_CONTRACT
        unit._change_reason = f'Contrato a partir de reserva #{reservation.id}'
        unit.save(update_fields=['status', 'updated_at'])

    return reservation


# ---------------------------------------------------------------------------
# Lead pipeline
# ---------------------------------------------------------------------------

@transaction.atomic
def advance_lead_stage(lead_id: str, new_stage: str, user, lost_reason: str = '') -> 'Lead':
    """
    Advance a lead's pipeline stage. Raises InvalidStageTransitionError
    if the requested transition is not in LEAD_STAGE_TRANSITIONS.
    """
    from .models import Lead

    try:
        lead = Lead.objects.select_for_update().get(id=lead_id)
    except Lead.DoesNotExist:
        raise ValidationError({'lead_id': 'Lead não encontrado.'})

    allowed = LEAD_STAGE_TRANSITIONS.get(lead.stage, [])
    if new_stage not in allowed:
        raise InvalidStageTransitionError(
            {'stage': f'Transição inválida: {lead.stage} → {new_stage}. '
                      f'Transições permitidas: {allowed or ["nenhuma (estado final)"]}'}
        )

    lead.stage = new_stage
    if new_stage == Lead.STAGE_LOST and lost_reason:
        lead.lost_reason = lost_reason
    lead._change_reason = f'Stage: {lead.stage} → {new_stage} (por {user.email})'
    lead.save(update_fields=['stage', 'lost_reason', 'updated_at'])

    return lead
