---
name: cabo-verde-context
description: Cabo Verde real estate specifics — CVE currency, pt-PT language, MBE payments, neighborhoods, Lei 133/V/2019. Auto-load when handling pricing, localisation, legal compliance, or geographic data.
argument-hint: [topic] [audience]
allowed-tools: Read
---

# Cabo Verde Context — ImoOS

## Purpose
Ground all features in Cabo Verde's legal, financial, and cultural specifics.

## Currency & Pricing
```python
# CVE is primary. EUR is derived (fixed peg: 1 EUR = 110.265 CVE)
class UnitPricing(models.Model):
    price_cve = models.DecimalField(max_digits=12, decimal_places=2)
    price_eur = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    EUR_CVE_RATE = Decimal('110.265')  # BCV fixed peg

    def sync_eur(self):
        self.price_eur = (self.price_cve / self.EUR_CVE_RATE).quantize(Decimal('0.01'))
```

## MBE Payment Reference
```python
def generate_mbe_reference(entity_code: str, invoice_id: int) -> str:
    """Cabo Verde Multibanco payment reference format."""
    return f"{entity_code} {str(invoice_id).zfill(9)}"
```

## Language & Formatting
- Default locale: `pt-PT` (European Portuguese — "projecto" not "projeto")
- Date format: `DD/MM/YYYY`
- Number format: `1.234,56` (dot for thousands, comma for decimals)
- Timezone: `Atlantic/Cape_Verde` (UTC-1)

## Key Rules
- Always store price in CVE — EUR is display-only
- MBE payments require entity code + 9-digit reference
- Consent fields (marketing + data processing) required for all buyer records (Lei 133/V/2019)
- Design for intermittent connectivity — Praia coverage can be unreliable

## Geographic Reference
- Islands: Santiago (Praia), São Vicente (Mindelo), Sal (Santa Maria), Fogo, Boa Vista
- Praia neighborhoods: Achada Santo António, Plateau, Várzea, Palmarejo, Terra Branca
- Mindelo neighborhoods: Centro, Ribeira Bote, Calhau, Lazareto

## Anti-Patterns
- Never use `pt-BR` locale or BRL currency
- Never hard-code a floating EUR/CVE rate (it's a fixed peg by BCV)
- Never send WhatsApp templates without Meta pre-approval
