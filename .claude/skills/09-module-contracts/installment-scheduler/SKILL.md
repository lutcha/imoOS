---
name: installment-scheduler
description: Task Celery beat diária que verifica prestações próximas e envia lembretes WhatsApp a 30d/7d/1d antes do vencimento. Usa idempotência para evitar duplicados.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Garantir que os compradores recebem lembretes de pagamento atempados via WhatsApp. A idempotência é garantida por um campo de controlo que regista quais lembretes já foram enviados para cada prestação.

## Code Pattern

```python
# contracts/models.py
from django.db import models

class Installment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        PAID = "PAID", "Pago"
        PARTIAL = "PARTIAL", "Parcialmente Pago"
        OVERDUE = "OVERDUE", "Em Atraso"
        CANCELLED = "CANCELLED", "Cancelado"

    contract = models.ForeignKey("Contract", on_delete=models.CASCADE, related_name="installments")
    sequence = models.PositiveIntegerField()
    description = models.CharField(max_length=255)
    amount_cve = models.DecimalField(max_digits=14, decimal_places=2)
    paid_amount_cve = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Idempotência: controlo de lembretes enviados
    reminder_30d_sent = models.BooleanField(default=False)
    reminder_7d_sent = models.BooleanField(default=False)
    reminder_1d_sent = models.BooleanField(default=False)
```

```python
# contracts/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_installment_reminders():
    """
    Executa diariamente às 09:00.
    Verifica prestações nos próximos 30, 7 e 1 dia e envia lembretes WhatsApp.
    """
    from .models import Installment

    today = timezone.now().date()

    reminders = [
        (30, "reminder_30d_sent", "30 dias"),
        (7,  "reminder_7d_sent",  "7 dias"),
        (1,  "reminder_1d_sent",  "1 dia"),
    ]

    for days_ahead, flag_field, label in reminders:
        target_date = today + timedelta(days=days_ahead)
        installments = Installment.objects.filter(
            due_date=target_date,
            status=Installment.Status.PENDING,
            **{flag_field: False},
        ).select_related("contract__buyer")

        for installment in installments:
            _send_reminder_whatsapp(installment, label)
            # Marcar como enviado (idempotência)
            setattr(installment, flag_field, True)
            installment.save(update_fields=[flag_field])


def _send_reminder_whatsapp(installment, days_label: str):
    buyer = installment.contract.buyer
    msg = (
        f"Olá {buyer.full_name}, a sua prestação de "
        f"{installment.amount_cve:,.0f} CVE vence em {days_label} "
        f"({installment.due_date.strftime('%d/%m/%Y')}). "
        "Por favor, efetue o pagamento atempadamente."
    )
    # send_whatsapp(buyer.phone, msg)
```

```python
# settings/celery.py
CELERY_BEAT_SCHEDULE = {
    "send-installment-reminders": {
        "task": "contracts.tasks.send_installment_reminders",
        "schedule": crontab(hour=9, minute=0),
    },
}
```

## Key Rules

- Os campos `reminder_Xd_sent` garantem idempotência mesmo que a task corra múltiplas vezes no mesmo dia.
- Verificar exatamente o `due_date == target_date` (não intervalo) para evitar duplicados entre dias.
- Apenas enviar lembretes para prestações com `status=PENDING` — nunca para `PAID` ou `OVERDUE`.
- Registar cada lembrete enviado em `NotificationLog` para auditoria.

## Anti-Pattern

```python
# ERRADO: usar filtro de intervalo sem flag de idempotência
Installment.objects.filter(due_date__lte=today + timedelta(days=30)).update(...)
# Envia o mesmo lembrete todos os dias durante 30 dias
```
