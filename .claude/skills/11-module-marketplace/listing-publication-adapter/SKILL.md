---
name: listing-publication-adapter
description: Transforma Unit + UnitPricing no payload JSON do imo.cv, tabela de mapeamento de campos, POST para IMO_CV_API_URL/listings e retorno de external_listing_id.
argument-hint: "[unit_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Adaptar os dados internos de unidades ImoOS para o formato de publicação do portal imo.cv. O padrão Adapter isola a lógica de mapeamento, facilitando a manutenção quando a API externa muda.

## Code Pattern

```python
# marketplace/adapters.py
from decimal import Decimal

# Mapeamento de campos ImoOS → imo.cv
UNIT_TYPE_MAP = {
    "T0": "studio",
    "T1": "t1",
    "T2": "t2",
    "T3": "t3",
    "T4": "t4_plus",
    "COMMERCIAL": "commercial",
    "PARKING": "parking",
}

STATUS_MAP = {
    "AVAILABLE": "available",
    "RESERVED": "reserved",
    "CONTRACT": "reserved",
    "SOLD": "sold",
    "SUSPENDED": "unavailable",
}

def unit_to_imo_cv_payload(unit) -> dict:
    """Transforma Unit + UnitPricing no payload do imo.cv."""
    pricing = getattr(unit, "pricing", None)
    project = unit.project

    return {
        "external_id": str(unit.id),
        "title": f"{unit.get_type_display()} | {project.name} | {unit.code}",
        "type": UNIT_TYPE_MAP.get(unit.type, "other"),
        "status": STATUS_MAP.get(unit.status, "unavailable"),
        "price": int(pricing.price_cve) if pricing else None,
        "currency": "CVE",
        "area_gross": float(unit.area_bruta),
        "area_net": float(unit.area_util) if unit.area_util else None,
        "floor": unit.floor,
        "bedrooms": _bedrooms_from_type(unit.type),
        "location": {
            "project_name": project.name,
            "island": project.island,
            "lat": float(project.location_point.y) if project.location_point else None,
            "lon": float(project.location_point.x) if project.location_point else None,
        },
        "images": [m.url for m in unit.media.all()[:10]],
        "developer": {"name": unit.project.tenant.name},
    }


def _bedrooms_from_type(unit_type: str) -> int | None:
    mapping = {"T0": 0, "T1": 1, "T2": 2, "T3": 3, "T4": 4}
    return mapping.get(unit_type)
```

```python
# marketplace/services.py
import requests
from django.conf import settings

def publish_listing(unit) -> str:
    """Publica unidade no imo.cv e retorna external_listing_id."""
    payload = unit_to_imo_cv_payload(unit)
    response = requests.post(
        f"{settings.IMO_CV_API_URL}/listings/",
        json=payload,
        headers={"Authorization": f"Bearer {settings.IMO_CV_API_TOKEN}"},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    external_id = data["id"]
    unit.external_listing_id = external_id
    unit.save(update_fields=["external_listing_id"])
    return external_id
```

## Key Rules

- O `unit_to_imo_cv_payload()` deve ser a única função que conhece o formato do imo.cv — isolar completamente.
- Mapear `unit.status` para o formato imo.cv: `CONTRACT` → `reserved` (não existe "contract" no portal).
- Guardar `external_listing_id` na unidade imediatamente após publicação bem-sucedida.
- Lançar exceção descritiva se campos obrigatórios (tipo, preço) estiverem em falta.

## Anti-Pattern

```python
# ERRADO: incluir lógica de mapeamento inline em múltiplos sítios
payload = {"type": "t2", "price": unit.pricing.price_cve, ...}  # duplicação — difícil de manter
```
