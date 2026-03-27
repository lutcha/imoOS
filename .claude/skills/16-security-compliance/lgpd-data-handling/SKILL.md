---
name: lgpd-data-handling
description: Conformidade com a Lei 133/V/2019 (proteção de dados Cabo Verde): campos de consentimento no modelo Buyer, comando anonymize_buyer() que anula PII mantendo registos financeiros, endpoint de exportação de dados.
argument-hint: "[buyer_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Garantir conformidade com a Lei 133/V/2019 (equivalente ao RGPD em Cabo Verde) no tratamento de dados pessoais de compradores. O sistema deve suportar o direito ao esquecimento e à portabilidade de dados.

## Code Pattern

```python
# crm/models.py
from django.db import models

class Buyer(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    nif = models.CharField(max_length=20, blank=True, verbose_name="NIF/BI")
    address = models.TextField(blank=True)
    nationality = models.CharField(max_length=100, blank=True)

    # Campos de consentimento Lei 133/V/2019
    consent_marketing = models.BooleanField(default=False)
    consent_data_processing = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    consent_ip = models.GenericIPAddressField(null=True, blank=True)

    # Estado de privacidade
    is_anonymized = models.BooleanField(default=False)
    anonymized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Comprador"
```

```python
# management/commands/anonymize_buyer.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

class Command(BaseCommand):
    help = "Anonimiza PII de comprador conforme Lei 133/V/2019 (direito ao esquecimento)"

    def add_arguments(self, parser):
        parser.add_argument("buyer_id", type=int)
        parser.add_argument("--confirm", action="store_true", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        from crm.models import Buyer
        from audit.services import log_action

        buyer = Buyer.objects.get(id=options["buyer_id"])

        if buyer.is_anonymized:
            self.stdout.write(self.style.WARNING(f"Comprador #{buyer.id} já foi anonimizado."))
            return

        # Verificar que não há contratos activos
        if buyer.contracts.filter(status__in=["ACTIVE", "PENDING"]).exists():
            self.stderr.write("ERRO: Não é possível anonimizar comprador com contratos ativos.")
            return

        # Anonimizar PII — manter dados financeiros (obrigação legal 7 anos)
        buyer.full_name = f"[ANONIMIZADO-{buyer.id}]"
        buyer.email = None
        buyer.phone = ""
        buyer.nif = ""
        buyer.address = ""
        buyer.nationality = ""
        buyer.consent_ip = None
        buyer.is_anonymized = True
        buyer.anonymized_at = timezone.now()
        buyer.save()

        # Registar no log de auditoria (imutável)
        log_action(None, "ANONYMIZE_BUYER", resource_type="Buyer", resource_id=buyer.id,
                   details={"reason": "Pedido de eliminação — Art. 17 Lei 133/V/2019"})

        self.stdout.write(self.style.SUCCESS(f"Comprador #{buyer.id} anonimizado com sucesso."))
```

```python
# crm/views.py — endpoint de exportação de dados (portabilidade)
from rest_framework.views import APIView
from rest_framework.response import Response

class BuyerDataExportView(APIView):
    """GET /api/v1/crm/buyers/{id}/data-export/ — direito à portabilidade"""

    def get(self, request, buyer_id):
        from .models import Buyer
        buyer = Buyer.objects.prefetch_related("contracts", "contracts__installments").get(
            id=buyer_id
        )
        # Apenas o próprio comprador ou ADMIN podem exportar
        if request.user.id != buyer.user_id and not request.user.is_staff:
            return Response(status=403)

        data = {
            "personal_data": {
                "full_name": buyer.full_name,
                "email": buyer.email,
                "phone": buyer.phone,
                "nif": buyer.nif,
            },
            "consents": {
                "marketing": buyer.consent_marketing,
                "data_processing": buyer.consent_data_processing,
                "date": buyer.consent_date.isoformat() if buyer.consent_date else None,
            },
            "contracts": [...],
        }
        return Response(data, headers={"Content-Disposition": f"attachment; filename=meus_dados_{buyer_id}.json"})
```

## Key Rules

- O consentimento (`consent_data_processing=True`) é obrigatório antes de recolher dados pessoais.
- A anonimização mantém registos financeiros e referências de contrato — apenas PII é apagado.
- O log de auditoria de anonimização é imutável — registo legal do cumprimento do pedido de eliminação.
- O prazo legal de retenção de dados financeiros em Cabo Verde é de 7 anos — não eliminar antes.

## Anti-Pattern

```python
# ERRADO: eliminar o registo do comprador completamente
Buyer.objects.filter(id=buyer_id).delete()  # perde dados financeiros necessários para auditoria legal
```
