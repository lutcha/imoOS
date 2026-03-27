---
name: sales-pipeline-kanban
description: Endpoint API que retorna {stage, leads:[{id, buyer_name, unit_code, value_cve, days_in_stage}]}, métricas conversion_rate e avg_days_to_close.
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Fornecer os dados do pipeline de vendas em formato Kanban. O endpoint é otimizado para renderização no frontend com todas as métricas calculadas no servidor para evitar lógica duplicada no cliente.

## Code Pattern

```python
# crm/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Count, F, ExpressionWrapper, DurationField

class SalesPipelineKanbanView(APIView):
    """GET /api/v1/crm/pipeline/kanban/?project_id=1"""

    STAGES = ["NEW", "CONTACTED", "QUALIFIED", "PROPOSAL", "NEGOTIATION"]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        from .models import Lead, LeadStatus

        qs = Lead.objects.filter(project_id=project_id).exclude(
            status__in=[LeadStatus.WON, LeadStatus.LOST]
        ).select_related("assigned_to")

        pipeline = []
        for stage in self.STAGES:
            stage_leads = qs.filter(status=stage)
            leads_data = []
            for lead in stage_leads:
                days = (timezone.now() - lead.status_updated_at).days if hasattr(lead, "status_updated_at") else 0
                leads_data.append({
                    "id": lead.id,
                    "buyer_name": lead.full_name,
                    "unit_code": lead.interested_unit.code if lead.interested_unit_id else None,
                    "value_cve": float(lead.budget_max) if lead.budget_max else None,
                    "days_in_stage": days,
                    "agent": lead.assigned_to.get_full_name() if lead.assigned_to else None,
                    "score": lead.score,
                })
            pipeline.append({"stage": stage, "count": len(leads_data), "leads": leads_data})

        metrics = self._calculate_metrics(project_id)
        return Response({"pipeline": pipeline, "metrics": metrics})

    def _calculate_metrics(self, project_id: int) -> dict:
        from .models import Lead, LeadStatus
        from django.db.models import Q

        base = Lead.objects.filter(project_id=project_id)
        total = base.count()
        won = base.filter(status=LeadStatus.WON).count()
        lost = base.filter(status=LeadStatus.LOST).count()

        closed = won + lost
        conversion_rate = (won / closed * 100) if closed > 0 else 0

        avg_days = base.filter(
            status=LeadStatus.WON,
            won_at__isnull=False,
        ).annotate(
            days_to_close=ExpressionWrapper(
                F("won_at") - F("created_at"),
                output_field=DurationField()
            )
        ).aggregate(avg=Avg("days_to_close"))["avg"]

        return {
            "total_leads": total,
            "won": won,
            "lost": lost,
            "conversion_rate": round(conversion_rate, 1),
            "avg_days_to_close": avg_days.days if avg_days else None,
        }
```

## Key Rules

- O endpoint deve retornar apenas leads ativos (excluir WON e LOST do Kanban visual).
- `days_in_stage` requer o campo `status_updated_at` no modelo Lead — adicionar ao modelo.
- Otimizar com `select_related` e `prefetch_related` para evitar N+1 queries.
- Limitar o Kanban a 50 leads por etapa para performance — incluir paginação por etapa se necessário.

## Anti-Pattern

```python
# ERRADO: calcular days_in_stage no frontend com base em timestamps do histórico
# Causa inconsistências de fuso horário e múltiplas chamadas à API
```
