---
name: analytics-conversion-tracking
description: Rastrear visualizações/leads/visitas/reservas/vendas por canal. Endpoint de funil de conversão retornando {channel, views, leads, visits, reservations, sales, conversion_rate}.
argument-hint: "[project_id] [date_from] [date_to]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Medir a eficácia de cada canal de aquisição ao longo do funil de vendas completo. Os dados permitem otimizar o investimento em marketing e identificar onde os leads se perdem.

## Code Pattern

```python
# marketplace/models.py
from django.db import models

class ListingView(models.Model):
    unit = models.ForeignKey("inventory.Unit", on_delete=models.CASCADE, related_name="views")
    source = models.CharField(max_length=50)  # 'IMO_CV', 'WEBSITE', 'DIRECT'
    session_id = models.CharField(max_length=100, blank=True)
    ip_hash = models.CharField(max_length=64, blank=True)  # SHA-256 do IP para anonimização
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["unit", "source", "viewed_at"]),
        ]
```

```python
# marketplace/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count

class ConversionFunnelView(APIView):
    """GET /api/v1/marketplace/analytics/funnel/?project_id=1&from=2025-01-01&to=2025-12-31"""

    CHANNELS = ["IMO_CV", "WEBSITE", "WALK_IN", "REFERRAL", "PHONE", "SOCIAL"]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        date_from = request.query_params.get("from")
        date_to = request.query_params.get("to")

        result = []
        for channel in self.CHANNELS:
            funnel = self._calculate_funnel(project_id, channel, date_from, date_to)
            result.append(funnel)

        return Response({
            "funnel": result,
            "summary": self._calculate_summary(result),
        })

    def _calculate_funnel(self, project_id, channel, date_from, date_to) -> dict:
        from inventory.models import Unit
        from crm.models import Lead, Visit
        from crm.models import Reservation

        views = ListingView.objects.filter(
            unit__project_id=project_id, source=channel,
            viewed_at__date__gte=date_from, viewed_at__date__lte=date_to,
        ).count()

        leads = Lead.objects.filter(
            project_id=project_id, source=channel,
            created_at__date__gte=date_from, created_at__date__lte=date_to,
        ).count()

        visits = Visit.objects.filter(
            lead__project_id=project_id, lead__source=channel,
            scheduled_at__date__gte=date_from, scheduled_at__date__lte=date_to,
        ).count()

        reservations = Reservation.objects.filter(
            lead__project_id=project_id, lead__source=channel,
            created_at__date__gte=date_from,
        ).count()

        sales = Lead.objects.filter(
            project_id=project_id, source=channel, status="WON",
        ).count()

        return {
            "channel": channel,
            "views": views,
            "leads": leads,
            "visits": visits,
            "reservations": reservations,
            "sales": sales,
            "conversion_rate": round(sales / leads * 100, 1) if leads > 0 else 0,
        }

    def _calculate_summary(self, channels: list) -> dict:
        total_leads = sum(c["leads"] for c in channels)
        total_sales = sum(c["sales"] for c in channels)
        return {
            "total_leads": total_leads,
            "total_sales": total_sales,
            "overall_conversion_rate": round(total_sales / total_leads * 100, 1) if total_leads > 0 else 0,
        }
```

## Key Rules

- Anonimizar IPs com SHA-256 antes de guardar em `ListingView` — conformidade LGPD.
- Cachear o endpoint em Redis com TTL de 30 minutos — evitar queries pesadas a cada pedido.
- `conversion_rate` = `sales / leads × 100` — não usar `views` como denominador (muito volátil).
- O relatório deve restringir-se a utilizadores com papel `MANAGER`, `ADMIN` ou `INVESTOR`.

## Anti-Pattern

```python
# ERRADO: calcular conversion_rate como views→sales
conversion_rate = sales / views * 100  # taxa irrealisticamente baixa — enganosa para o cliente
```
