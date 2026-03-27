---
name: progress-measurement-wbs
description: Atualização de progresso WBS via mobile, cálculo de valor ganho (EV = orçamento × progresso%), endpoint S-curve retornando {week, planned_pct, actual_pct}.
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Medir o progresso físico de obra por tarefa WBS a partir do dispositivo móvel. O cálculo de valor ganho (Earned Value) permite comparar progresso real vs. planeado. A curva S é a visualização padrão para o cliente/investidor.

## Code Pattern

```python
# construction/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

class WBSProgressUpdateSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    progress_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    notes = serializers.CharField(required=False, allow_blank=True)

class WBSProgressUpdateView(APIView):
    """POST /api/v1/construction/wbs/progress/ — mobile friendly"""

    def post(self, request):
        ser = WBSProgressUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        from projects.models import WBSTask
        from projects.services import rollup_wbs_progress
        task = WBSTask.objects.get(id=ser.validated_data["task_id"])

        # Validar que é nó folha (só folhas têm progresso manual)
        if task.children.exists():
            return Response({"error": "Apenas tarefas folha podem ter progresso atualizado manualmente."}, status=400)

        old_progress = task.progress_percentage
        task.progress_percentage = ser.validated_data["progress_percentage"]
        task.save(update_fields=["progress_percentage"])

        # Rollup para nós pai
        rollup_wbs_progress(task.project_id)

        return Response({
            "task_id": task.id,
            "progress": float(task.progress_percentage),
            "ev_cve": float(task.budget_cve * task.progress_percentage / 100) if task.budget_cve else None,
        })
```

```python
# construction/views.py — S-Curve endpoint
from django.db.models import Avg
import datetime

class SCurveView(APIView):
    """GET /api/v1/construction/projects/{id}/s-curve/"""

    def get(self, request, project_id):
        from projects.models import Project, WBSTask
        project = Project.objects.get(id=project_id)

        start = project.start_date
        end = project.planned_end_date
        if not start or not end:
            return Response({"error": "Projeto sem datas definidas."}, status=400)

        weeks = []
        current = start
        while current <= end:
            week_end = current + datetime.timedelta(days=6)

            # Progresso planeado: % de tarefas com planned_end <= semana atual
            planned_tasks = WBSTask.objects.filter(
                project_id=project_id,
                planned_end__lte=week_end,
                parent__isnull=True,  # apenas nós raiz para simplificar
            )
            total_tasks = WBSTask.objects.filter(project_id=project_id, parent__isnull=True).count()
            planned_pct = (planned_tasks.count() / total_tasks * 100) if total_tasks else 0

            # Progresso real: média de progresso_percentage em todas as tarefas
            actual_pct = WBSTask.objects.filter(
                project_id=project_id
            ).aggregate(avg=Avg("progress_percentage"))["avg"] or 0

            weeks.append({
                "week": current.isoformat(),
                "planned_pct": round(planned_pct, 1),
                "actual_pct": round(float(actual_pct), 1),
            })
            current += datetime.timedelta(days=7)

        return Response({"s_curve": weeks})
```

## Key Rules

- Apenas tarefas folha (sem filhos) aceitam atualização manual de progresso.
- Chamar `rollup_wbs_progress()` após cada atualização para manter os nós pai consistentes.
- EV = `budget_cve × (progress_percentage / 100)` — `budget_cve` deve existir em `WBSTask`.
- O endpoint S-Curve deve ser cacheado em Redis (TTL 15 min) — é computacionalmente intenso.

## Anti-Pattern

```python
# ERRADO: atualizar progresso de nó pai diretamente sem rollup
task.progress_percentage = 75
task.save()  # nós pai ficam inconsistentes com os filhos
```
