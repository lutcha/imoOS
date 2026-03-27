---
name: project-milestone-tracking
description: Modelo Milestone com planned_date/actual_date/status e endpoint de dados para gráfico de Gantt retornando {id, name, start, end, progress}.
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Rastrear marcos de projetos com datas planeadas e reais. O endpoint de Gantt fornece dados estruturados prontos para renderização em bibliotecas como DHTMLX Gantt ou React Gantt Chart.

## Code Pattern

```python
# projects/models.py
from django.db import models

class Milestone(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        IN_PROGRESS = "IN_PROGRESS", "Em Progresso"
        COMPLETED = "COMPLETED", "Concluído"
        DELAYED = "DELAYED", "Atrasado"

    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="milestones")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    planned_date = models.DateField()
    actual_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    predecessor = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="successors"
    )

    class Meta:
        ordering = ["planned_date"]

    def is_delayed(self) -> bool:
        from django.utils import timezone
        return (
            self.status != self.Status.COMPLETED
            and self.planned_date < timezone.now().date()
        )
```

```python
# projects/views.py
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Milestone

class GanttDataView(APIView):
    """GET /api/v1/projects/{id}/gantt/ — dados para gráfico de Gantt"""

    def get(self, request, project_id):
        milestones = Milestone.objects.filter(project_id=project_id).select_related("predecessor")

        tasks = []
        for m in milestones:
            tasks.append({
                "id": m.id,
                "name": m.name,
                "start": m.planned_date.isoformat(),
                "end": (m.actual_date or m.planned_date).isoformat(),
                "progress": float(m.progress_percentage),
                "status": m.status,
                "predecessor_id": m.predecessor_id,
                "is_delayed": m.is_delayed(),
            })

        return Response({"tasks": tasks})
```

## Key Rules

- `actual_date` só deve ser preenchida quando `status=COMPLETED`; usar `null` enquanto em progresso.
- Atualizar `status` para `DELAYED` via task Celery beat diária quando `planned_date` ultrapassado e não concluído.
- O campo `predecessor` permite modelar dependências para o Gantt; respeitar esta ordem nas notificações.
- Incluir `is_delayed` no payload do Gantt para o frontend destacar visualmente os atrasos.

## Anti-Pattern

```python
# ERRADO: calcular atrasos no frontend comparando datas
# O backend deve expor is_delayed para evitar lógica duplicada e fusos horários incorretos
```
