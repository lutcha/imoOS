---
name: lead-source-tracking
description: Modelo Lead com enum de fonte (IMO_CV/WALK_IN/REFERRAL/PHONE/SOCIAL), parsing de parâmetros UTM na criação e endpoint de relatório de atribuição.
argument-hint: "[date_from] [date_to]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Rastrear a origem de cada lead para medir a eficácia de cada canal de aquisição. Os parâmetros UTM são capturados na criação do lead e persistidos para análise de atribuição.

## Code Pattern

```python
# crm/models.py
from django.db import models

class LeadSource(models.TextChoices):
    IMO_CV = "IMO_CV", "Portal imo.cv"
    WALK_IN = "WALK_IN", "Visita Direta"
    REFERRAL = "REFERRAL", "Referência"
    PHONE = "PHONE", "Telefone"
    SOCIAL = "SOCIAL", "Redes Sociais"
    WEBSITE = "WEBSITE", "Website"
    OTHER = "OTHER", "Outro"

class Lead(models.Model):
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    source = models.CharField(max_length=20, choices=LeadSource.choices)

    # UTM tracking
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    utm_content = models.CharField(max_length=100, blank=True)
    referrer_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.SET_NULL
    )
```

```python
# crm/serializers.py
from rest_framework import serializers
from .models import Lead, LeadSource

class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            "project", "full_name", "email", "phone", "source",
            "utm_source", "utm_medium", "utm_campaign", "utm_content", "referrer_url",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            _parse_utm_from_request(validated_data, request)
        return super().create(validated_data)

def _parse_utm_from_request(data: dict, request) -> None:
    for param in ["utm_source", "utm_medium", "utm_campaign", "utm_content"]:
        if param not in data:
            data[param] = request.query_params.get(param, "")
    if not data.get("referrer_url"):
        data["referrer_url"] = request.META.get("HTTP_REFERER", "")
```

```python
# crm/views.py — relatório de atribuição
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response

class LeadAttributionReportView(APIView):
    """GET /api/v1/crm/reports/attribution/?from=2025-01-01&to=2025-12-31"""

    def get(self, request):
        qs = Lead.objects.filter(
            created_at__date__gte=request.query_params.get("from"),
            created_at__date__lte=request.query_params.get("to"),
        )
        by_source = qs.values("source").annotate(count=Count("id")).order_by("-count")
        by_campaign = qs.exclude(utm_campaign="").values("utm_campaign").annotate(count=Count("id"))
        return Response({"by_source": list(by_source), "by_campaign": list(by_campaign)})
```

## Key Rules

- Capturar parâmetros UTM no momento da criação do lead — não podem ser adicionados posteriormente.
- O campo `source` é obrigatório — nunca deixar `null`.
- `IMO_CV` como source deve preencher automaticamente o `external_lead_id` retornado pelo webhook do imo.cv.
- O relatório de atribuição deve ser restrito a utilizadores com papel `MANAGER` ou `ADMIN`.

## Anti-Pattern

```python
# ERRADO: ignorar UTM e guardar apenas a source genérica
Lead.objects.create(source="WEBSITE")  # perde-se toda a informação de campanha
```
