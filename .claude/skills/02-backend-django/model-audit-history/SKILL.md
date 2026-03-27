---
name: model-audit-history
description: Add django-simple-history to ImoOS models for immutable audit trail. Auto-load when creating or modifying transactional models (Unit, Project, Contract, Payment, Reservation).
argument-hint: [ModelName] [fields-to-track]
allowed-tools: Read, Write, Grep
---

# Model Audit History — ImoOS

## Adding HistoricalRecords to a Model
```python
from simple_history.models import HistoricalRecords

class Contract(models.Model):
    # ... fields ...
    history = HistoricalRecords()  # One line — tracks all field changes

# django creates a HistoricalContract table automatically
```

## Required Models (MANDATORY per blueprint)
Every change to these models must be tracked:
- `Project` ✅ (status, dates, budget)
- `Unit` ✅ (status transitions, code changes)
- `UnitPricing` ✅ (price history is a legal/financial requirement)
- `Contract` (add in Sprint 3)
- `Payment` (add in Sprint 3)
- `Reservation` (add in Sprint 2)

## Querying History
```python
# Get all changes to a unit
unit = Unit.objects.get(id=unit_id)
for record in unit.history.all():
    print(f"{record.history_date}: {record.history_user} changed {record.history_type}")

# Get the diff between two versions
new = unit.history.first()
old = unit.history.filter(history_date__lt=new.history_date).first()
delta = new.diff_against(old)
for change in delta.changes:
    print(f"{change.field}: {change.old!r} → {change.new!r}")
```

## Storing Change Reason
```python
# In views/services — add reason for important changes
unit.status = 'RESERVED'
unit._change_reason = f'Reservado por {request.user.email}'
unit.save()
```

## Settings
```python
# config/settings/base.py
SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD = True
SIMPLE_HISTORY_REVERT_DISABLED = False  # Allow revert for admin use
```

## Key Rules
- `history = HistoricalRecords()` must be the last field in the model class
- Set `HistoryRequestMiddleware` in MIDDLEWARE for automatic user tracking
- Never delete historical records — they are an immutable audit trail
- For LGPD compliance: anonymize `history_user` display on erasure requests (keep the record, redact PII)
