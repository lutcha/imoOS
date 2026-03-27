---
name: dunning-automation
description: Sequência de cobrança: lembrete no dia 0, aviso no dia 7, notificação de suspensão no dia 30. Celery beat verifica prestações em atraso diariamente. Configurável por inquilino.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Automatizar o processo de cobrança de prestações em atraso com uma sequência de comunicações progressivamente mais formais. A configuração por inquilino permite adaptar os prazos às políticas comerciais de cada empresa.

## Code Pattern

```python
# contracts/models.py
from django.db import models

class DunningConfig(models.Model):
    """Configuração de cobrança por inquilino — um registo por schema."""
    reminder_day = models.IntegerField(default=0,   help_text="Dias após vencimento para lembrete")
    warning_day  = models.IntegerField(default=7,   help_text="Dias após vencimento para aviso")
    suspend_day  = models.IntegerField(default=30,  help_text="Dias após vencimento para notificação de suspensão")
    suspend_enabled = models.BooleanField(default=True)

    class Meta:
        app_label = "contracts"


class DunningLog(models.Model):
    class Action(models.TextChoices):
        REMINDER = "REMINDER", "Lembrete"
        WARNING   = "WARNING",  "Aviso"
        SUSPEND   = "SUSPEND",  "Suspensão"

    installment = models.ForeignKey("Installment", on_delete=models.CASCADE, related_name="dunning_logs")
    action = models.CharField(max_length=20, choices=Action.choices)
    sent_at = models.DateTimeField(auto_now_add=True)
    channel = models.CharField(max_length=20, default="WHATSAPP")
```

```python
# contracts/tasks.py
from celery import shared_task
from django.utils import timezone

@shared_task
def process_dunning_sequence():
    """Executa diariamente às 10:00 — verifica prestações em atraso."""
    from .models import Installment, DunningConfig, DunningLog

    config = DunningConfig.objects.first() or DunningConfig()
    today = timezone.now().date()

    overdue = Installment.objects.filter(
        due_date__lt=today,
        status__in=[Installment.Status.PENDING, Installment.Status.PARTIAL],
    ).select_related("contract__buyer")

    for installment in overdue:
        days_overdue = (today - installment.due_date).days
        _process_installment_dunning(installment, days_overdue, config, DunningLog)


def _process_installment_dunning(installment, days_overdue, config, DunningLog):
    from .models import DunningLog as DL
    buyer = installment.contract.buyer

    actions_to_check = [
        (config.reminder_day, DL.Action.REMINDER),
        (config.warning_day,  DL.Action.WARNING),
        (config.suspend_day,  DL.Action.SUSPEND),
    ]

    for threshold, action in actions_to_check:
        if days_overdue >= threshold:
            already_sent = DL.objects.filter(
                installment=installment, action=action
            ).exists()
            if not already_sent:
                _send_dunning_message(buyer, installment, action, days_overdue)
                DL.objects.create(installment=installment, action=action)
                if action == DL.Action.SUSPEND and config.suspend_enabled:
                    _flag_for_suspension(installment.contract)
                break  # Enviar apenas o mais severo ainda não enviado


def _send_dunning_message(buyer, installment, action, days_overdue):
    messages = {
        "REMINDER": f"A sua prestação de {installment.amount_cve:,.0f} CVE venceu hoje.",
        "WARNING": f"Atenção: {days_overdue} dias em atraso. Regularize o pagamento.",
        "SUSPEND": f"Prestação com {days_overdue} dias em atraso. O seu acesso pode ser suspenso.",
    }
    # send_whatsapp(buyer.phone, messages[action])
```

## Key Rules

- Usar `DunningLog` para garantir idempotência — cada ação só é enviada uma vez por prestação.
- A sequência é progressiva: enviar apenas a ação mais severa ainda não enviada.
- `suspend_enabled` permite desativar suspensão automática por inquilino.
- Marcar `installment.status = OVERDUE` na primeira execução da cobrança (dia 0).

## Anti-Pattern

```python
# ERRADO: enviar todos os níveis de cobrança de uma vez para prestações muito atrasadas
for action in ["REMINDER", "WARNING", "SUSPEND"]:
    send_dunning_message(buyer, action)  # bombardeia o cliente com 3 mensagens
```
