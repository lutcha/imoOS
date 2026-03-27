---
name: visit-scheduling-calendar
description: Modelo Visit com scheduled_at/actual_at/outcome, lembrete WhatsApp 24h antes e endpoint de calendário {date, visits_count, available_slots}.
argument-hint: "[agent_id] [date_from] [date_to]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir visitas a projetos e unidades com agendamento, registo de resultado e lembretes automáticos via WhatsApp. O endpoint de calendário permite ao frontend renderizar disponibilidade e ocupação por dia.

## Code Pattern

```python
# crm/models.py
from django.db import models

class VisitOutcome(models.TextChoices):
    PENDING = "PENDING", "Pendente"
    COMPLETED = "COMPLETED", "Realizada"
    NO_SHOW = "NO_SHOW", "Não Compareceu"
    CANCELLED = "CANCELLED", "Cancelada"
    RESCHEDULED = "RESCHEDULED", "Reagendada"

class Visit(models.Model):
    lead = models.ForeignKey("Lead", on_delete=models.CASCADE, related_name="visits")
    unit = models.ForeignKey("inventory.Unit", on_delete=models.SET_NULL, null=True, blank=True)
    agent = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    scheduled_at = models.DateTimeField()
    actual_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=60)
    outcome = models.CharField(max_length=20, choices=VisitOutcome.choices, default=VisitOutcome.PENDING)
    notes = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["scheduled_at"]
```

```python
# crm/tasks.py
from celery import shared_task
from celery.schedules import crontab
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_visit_reminders():
    """Executa de hora em hora; envia lembretes para visitas nas próximas 24h."""
    from .models import Visit, VisitOutcome
    window_start = timezone.now() + timedelta(hours=23)
    window_end = timezone.now() + timedelta(hours=25)

    visits = Visit.objects.filter(
        scheduled_at__range=(window_start, window_end),
        outcome=VisitOutcome.PENDING,
        reminder_sent=False,
    ).select_related("lead", "agent", "unit")

    for visit in visits:
        _send_whatsapp_reminder(visit)
        visit.reminder_sent = True
        visit.save(update_fields=["reminder_sent"])


def _send_whatsapp_reminder(visit):
    msg = (
        f"Olá {visit.lead.full_name}, lembra-se da sua visita amanhã "
        f"às {visit.scheduled_at.strftime('%H:%M')} "
        f"ao projeto {visit.unit.project.name if visit.unit else ''}? "
        "Aguardamos a sua presença!"
    )
    # send_whatsapp(visit.lead.phone, msg)
```

```python
# crm/views.py — endpoint de calendário
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count

class VisitCalendarView(APIView):
    """GET /api/v1/crm/visits/calendar/?from=2025-01-01&to=2025-01-31&agent_id=5"""
    SLOTS_PER_DAY = 8  # 8 visitas máximo por dia por agente

    def get(self, request):
        agent_id = request.query_params.get("agent_id")
        qs = Visit.objects.filter(
            scheduled_at__date__gte=request.query_params.get("from"),
            scheduled_at__date__lte=request.query_params.get("to"),
            agent_id=agent_id,
        )
        by_day = qs.values("scheduled_at__date").annotate(visits_count=Count("id"))

        return Response([{
            "date": row["scheduled_at__date"].isoformat(),
            "visits_count": row["visits_count"],
            "available_slots": max(0, self.SLOTS_PER_DAY - row["visits_count"]),
        } for row in by_day])
```

## Key Rules

- `reminder_sent=True` após envio para garantir idempotência — a task pode correr múltiplas vezes.
- `actual_at` apenas se preenche quando `outcome=COMPLETED` — nunca antes.
- `SLOTS_PER_DAY` deve ser configurável por agente ou em `TenantSettings`.
- Registar tentativas de contacto como atividade no lead após cada visita.

## Anti-Pattern

```python
# ERRADO: enviar lembretes sem verificar reminder_sent — duplica mensagens WhatsApp
Visit.objects.filter(scheduled_at__range=(...)).update(...)  # sem idempotência
```
