"""
Celery tasks for the inventory app.

Rules (CLAUDE.md):
- Always receive tenant_schema as a string argument, never ORM objects
- Use tenant_context() to switch schema before any DB operations
- Tasks must be idempotent: safe to re-run on the same data
"""
import csv
import io
import logging
from decimal import Decimal, InvalidOperation

from celery import shared_task
from django_tenants.utils import get_tenant_model, tenant_context

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CSV column reference
# ---------------------------------------------------------------------------
# Required: code, floor_id, unit_type_code, area_bruta
# Optional: description, area_util, orientation, floor_number,
#           price_cve, price_eur, discount_type, discount_value
#
# Idempotency key: (floor_id, code) — maps to Unit.unique_together

MAX_CSV_ROWS = 5_000


def _get_tenant(tenant_schema: str):
    TenantModel = get_tenant_model()
    return TenantModel.objects.get(schema_name=tenant_schema)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    time_limit=280,
    soft_time_limit=250,
    name='inventory.import_units_from_csv',
)
def import_units_from_csv(
    self,
    *,
    tenant_schema: str,
    csv_content: str,
    created_by_id: str | None = None,
) -> dict:
    """
    Bulk-import Unit rows from a CSV string into the given tenant schema.

    Returns::

        {
            "created": int,
            "updated": int,
            "errors": [{"row": int, "error": str}, ...]
        }
    """
    try:
        tenant = _get_tenant(tenant_schema)
    except Exception as exc:
        logger.error('import_units_from_csv: tenant %s not found: %s', tenant_schema, exc)
        raise self.retry(exc=exc)

    results: dict = {'created': 0, 'updated': 0, 'errors': []}

    with tenant_context(tenant):
        from django.contrib.auth import get_user_model

        from apps.inventory.models import Unit, UnitPricing, UnitType  # noqa: F401
        from apps.projects.models import Floor  # noqa: F401

        User = get_user_model()
        created_by = None
        if created_by_id:
            try:
                created_by = User.objects.get(id=created_by_id)
            except User.DoesNotExist:
                logger.warning('import_units_from_csv: created_by user %s not found', created_by_id)

        reader = csv.DictReader(io.StringIO(csv_content))
        for row_num, row in enumerate(reader, start=2):  # row 1 = header
            if row_num - 1 > MAX_CSV_ROWS:
                results['errors'].append({
                    'row': row_num,
                    'error': f'CSV exceeded maximum of {MAX_CSV_ROWS} rows.',
                })
                break
            try:
                _process_row(row, row_num, results, created_by)
            except Exception as exc:
                results['errors'].append({'row': row_num, 'error': str(exc)})

    logger.info(
        'import_units_from_csv tenant=%s created=%d updated=%d errors=%d',
        tenant_schema, results['created'], results['updated'], len(results['errors']),
    )
    return results


def _process_row(row: dict, row_num: int, results: dict, created_by) -> None:
    """Process one CSV row. Raises ValueError on validation failure."""
    from apps.inventory.models import Unit, UnitPricing, UnitType
    from apps.projects.models import Floor

    # --- Required fields ---
    code = row.get('code', '').strip()
    floor_id = row.get('floor_id', '').strip()
    unit_type_code = row.get('unit_type_code', '').strip()
    area_bruta_raw = row.get('area_bruta', '').strip()

    if not code:
        raise ValueError('Missing required field: code')
    if not floor_id:
        raise ValueError('Missing required field: floor_id')
    if not unit_type_code:
        raise ValueError('Missing required field: unit_type_code')
    if not area_bruta_raw:
        raise ValueError('Missing required field: area_bruta')

    try:
        area_bruta = Decimal(area_bruta_raw)
    except InvalidOperation:
        raise ValueError(f'Invalid area_bruta: {area_bruta_raw!r}')

    try:
        floor = Floor.objects.get(id=floor_id)
    except Floor.DoesNotExist:
        raise ValueError(f'Floor not found: {floor_id!r}')

    try:
        unit_type = UnitType.objects.get(code=unit_type_code)
    except UnitType.DoesNotExist:
        raise ValueError(f'UnitType not found for code: {unit_type_code!r}')

    # --- Optional fields ---
    area_util_raw = row.get('area_util', '').strip()
    area_util = Decimal(area_util_raw) if area_util_raw else None

    floor_number_raw = row.get('floor_number', '').strip()
    floor_number = int(floor_number_raw) if floor_number_raw else 0

    unit_defaults: dict = {
        'unit_type': unit_type,
        'description': row.get('description', '').strip(),
        'area_bruta': area_bruta,
        'area_util': area_util,
        'orientation': row.get('orientation', '').strip(),
        'floor_number': floor_number,
    }
    if created_by is not None:
        unit_defaults['created_by'] = created_by

    unit, created = Unit.objects.update_or_create(
        floor=floor,
        code=code,
        defaults=unit_defaults,
    )

    if created:
        results['created'] += 1
    else:
        results['updated'] += 1

    # --- Pricing (optional, only when price_cve is present) ---
    price_cve_raw = row.get('price_cve', '').strip()
    if not price_cve_raw:
        return

    try:
        price_cve = Decimal(price_cve_raw)
    except InvalidOperation:
        raise ValueError(f'Invalid price_cve: {price_cve_raw!r}')

    price_eur_raw = row.get('price_eur', '').strip()
    price_eur = Decimal(price_eur_raw) if price_eur_raw else None

    discount_type = row.get('discount_type', 'NONE').strip() or 'NONE'
    if discount_type not in ('NONE', 'PERCENT', 'FIXED'):
        discount_type = 'NONE'

    discount_value_raw = row.get('discount_value', '').strip()
    try:
        discount_value = Decimal(discount_value_raw) if discount_value_raw else Decimal('0.00')
    except InvalidOperation:
        discount_value = Decimal('0.00')

    UnitPricing.objects.update_or_create(
        unit=unit,
        defaults={
            'price_cve': price_cve,
            'price_eur': price_eur,
            'discount_type': discount_type,
            'discount_value': discount_value,
        },
    )
