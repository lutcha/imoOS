---
name: contract-template-engine
description: Modelo ContractTemplate com sintaxe de template Django, substituição de variáveis (buyer_name, unit_code, price_cve), versionamento e geração de PDF via WeasyPrint.
argument-hint: "[template_id] [contract_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir templates de contratos com versionamento e substituição dinâmica de variáveis. Cada inquilino pode ter os seus próprios templates com a sua marca. O PDF é gerado a partir do template renderizado.

## Code Pattern

```python
# contracts/models.py
from django.db import models

class ContractTemplate(models.Model):
    class TemplateType(models.TextChoices):
        SALE = "SALE", "Contrato de Compra e Venda"
        RESERVATION = "RESERVATION", "Contrato de Reserva"
        PROMISSORY = "PROMISSORY", "Contrato Promessa"

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TemplateType.choices)
    version = models.PositiveIntegerField(default=1)
    content = models.TextField(help_text="Suporta sintaxe de template Django: {{ buyer_name }}")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-version"]
        unique_together = ("type", "version")

    def render(self, context: dict) -> str:
        from django.template import Context, Template
        template = Template(self.content)
        return template.render(Context(context))
```

```python
# contracts/services.py
from weasyprint import HTML
from django.conf import settings
from decimal import Decimal

CVE_EUR_RATE = Decimal("110.265")

TEMPLATE_VARIABLES = {
    "buyer_name", "buyer_nif", "buyer_address",
    "unit_code", "unit_type", "unit_area",
    "price_cve", "price_eur", "price_words",
    "project_name", "contract_date", "notary_name",
}

def generate_contract_pdf(contract) -> bytes:
    template = ContractTemplate.objects.filter(
        type=contract.template_type, is_active=True
    ).order_by("-version").first()

    if not template:
        raise ValueError(f"Nenhum template ativo para o tipo {contract.template_type}")

    context = {
        "buyer_name": contract.buyer.full_name,
        "buyer_nif": contract.buyer.nif,
        "unit_code": contract.unit.code,
        "unit_type": contract.unit.type,
        "unit_area": str(contract.unit.area_bruta),
        "price_cve": f"{contract.unit.pricing.price_cve:,.0f}",
        "price_eur": f"{contract.unit.pricing.price_eur:,.2f}",
        "project_name": contract.unit.project.name,
        "contract_date": contract.signed_at.strftime("%d de %B de %Y") if contract.signed_at else "",
    }

    html_content = template.render(context)
    return HTML(string=html_content).write_pdf()
```

```python
# contracts/views.py — criar nova versão do template
class ContractTemplateVersionView(APIView):
    def post(self, request, template_id):
        old = ContractTemplate.objects.get(id=template_id)
        new = ContractTemplate.objects.create(
            name=old.name, type=old.type,
            version=old.version + 1,
            content=request.data["content"],
            created_by=request.user,
        )
        return Response({"id": new.id, "version": new.version}, status=201)
```

## Key Rules

- Nunca modificar um template existente — criar sempre uma nova versão com `version + 1`.
- Validar que todas as variáveis obrigatórias de `TEMPLATE_VARIABLES` estão presentes no contexto antes de renderizar.
- Apenas um template pode estar `is_active=True` por tipo — garantir via `unique_together` ou signal.
- Armazenar o PDF gerado em S3 com referência ao `version` do template usado.

## Anti-Pattern

```python
# ERRADO: usar str.format() ou f-strings para substituição de variáveis
html = template.content.format(**context)  # vulnerável a KeyError e sem suporte a filtros Django
```
