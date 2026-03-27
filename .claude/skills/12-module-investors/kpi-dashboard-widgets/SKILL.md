---
name: kpi-dashboard-widgets
description: Endpoints de widgets do dashboard: /kpis/cashflow/ (entradas/saídas mensais CVE), /kpis/roi/ (projetado vs real), /kpis/occupancy/ (% unidades vendidas), /kpis/units-sold/ (contagem por mês).
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Fornecer dados para os widgets do dashboard de investidores em endpoints dedicados e cacheados. Cada widget tem o seu endpoint independente para permitir carregamento paralelo e invalidação de cache granular.

## Code Pattern

```python
# investors/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Sum
from decimal import Decimal

CACHE_TTL = 900  # 15 minutos

def cached_kpi(cache_key_fn):
    def decorator(method):
        def wrapper(self, request, *args, **kwargs):
            key = cache_key_fn(request)
            data = cache.get(key)
            if data is None:
                data = method(self, request, *args, **kwargs).data
                cache.set(key, data, CACHE_TTL)
            return Response(data)
        return wrapper
    return decorator


class CashflowKPIView(APIView):
    """GET /api/v1/investors/kpis/cashflow/?project_id=1&months=12"""

    def get(self, request):
        project_id = request.query_params.get("project_id")
        months = int(request.query_params.get("months", 12))

        from django.utils import timezone
        from datetime import timedelta
        from contracts.models import Payment, Installment

        result = []
        today = timezone.now().date()
        for i in range(months - 1, -1, -1):
            period = today.replace(day=1) - timedelta(days=i * 30)
            month_start = period.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1)

            inflows = Payment.objects.filter(
                installment__contract__unit__project_id=project_id,
                payment_date__gte=month_start, payment_date__lt=month_end,
            ).aggregate(total=Sum("amount_cve"))["total"] or Decimal("0")

            result.append({
                "month": month_start.strftime("%Y-%m"),
                "inflows_cve": float(inflows),
                "outflows_cve": 0,  # TODO: integrar despesas de construção
            })

        return Response({"cashflow": result})


class ROIKPIView(APIView):
    """GET /api/v1/investors/kpis/roi/?project_id=1"""

    def get(self, request):
        from projects.models import Project
        from investors.models import Investor
        from inventory.models import Unit

        project = Project.objects.get(id=request.query_params.get("project_id"))
        total_invested = Investor.objects.filter(project=project).aggregate(
            total=Sum("investment_amount_cve")
        )["total"] or Decimal("0")

        sold_revenue = Unit.objects.filter(
            project=project, status="SOLD"
        ).select_related("pricing").aggregate(
            total=Sum("pricing__price_cve")
        )["total"] or Decimal("0")

        actual_roi = ((sold_revenue - total_invested) / total_invested * 100) if total_invested else Decimal("0")
        projected_roi = actual_roi * Decimal("1.2")  # simplificado — usar modelo financeiro real

        return Response({
            "total_invested_cve": float(total_invested),
            "revenue_cve": float(sold_revenue),
            "actual_roi_pct": float(actual_roi.quantize(Decimal("0.01"))),
            "projected_roi_pct": float(projected_roi.quantize(Decimal("0.01"))),
        })
```

```python
class OccupancyKPIView(APIView):
    """GET /api/v1/investors/kpis/occupancy/?project_id=1"""

    def get(self, request):
        from inventory.models import Unit
        qs = Unit.objects.filter(project_id=request.query_params.get("project_id"))
        total = qs.count()
        sold = qs.filter(status="SOLD").count()
        return Response({
            "total_units": total,
            "sold_units": sold,
            "occupancy_rate_pct": round(sold / total * 100, 1) if total else 0,
        })
```

## Key Rules

- Cachear todos os KPIs em Redis com TTL de 15 minutos — evitar queries pesadas a cada refresh.
- Invalidar o cache quando dados relevantes mudam (ex: nova venda) via `cache.delete(key)` no sinal `post_save`.
- Cada widget tem endpoint independente para permitir carregamento paralelo no frontend.
- Os KPIs de ROI devem usar sempre `Decimal` — nunca `float` em cálculos financeiros.

## Anti-Pattern

```python
# ERRADO: um endpoint monolítico que calcula todos os KPIs — lento e difícil de cachear granularmente
def get_all_kpis(request):
    return Response({"cashflow": ..., "roi": ..., "occupancy": ...})
```
