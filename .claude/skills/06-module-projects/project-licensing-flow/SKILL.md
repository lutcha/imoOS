---
name: project-licensing-flow
description: Modelo License com type/submitted_date/approved_date/expiry_date e task Celery beat para alertas 30 dias antes do vencimento.
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir o ciclo de vida das licenças de construção e habitação de projetos. A task periódica garante que os gestores são alertados atempadamente antes do vencimento, evitando paragens de obra por licenças expiradas.

## Code Pattern

```python
# projects/models.py
from django.db import models

class LicenseType(models.TextChoices):
    CONSTRUCTION = "CONSTRUCTION", "Licença de Construção"
    HABITATION = "HABITATION", "Licença de Habitação"
    ENVIRONMENTAL = "ENVIRONMENTAL", "Licença Ambiental"
    COMMERCIAL = "COMMERCIAL", "Licença Comercial"

class LicenseStatus(models.TextChoices):
    DRAFT = "DRAFT", "Rascunho"
    SUBMITTED = "SUBMITTED", "Submetido"
    APPROVED = "APPROVED", "Aprovado"
    REJECTED = "REJECTED", "Rejeitado"
    EXPIRED = "EXPIRED", "Expirado"

class License(models.Model):
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="licenses")
    type = models.CharField(max_length=20, choices=LicenseType.choices)
    reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=LicenseStatus.choices, default=LicenseStatus.DRAFT)
    submitted_date = models.DateField(null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    document = models.URLField(blank=True)  # URL no S3
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["expiry_date"]
```

```python
# projects/tasks.py
from celery import shared_task
from celery.schedules import crontab
from django.utils import timezone
from datetime import timedelta

@shared_task
def check_license_expiry():
    """Executa diariamente às 08:00 UTC."""
    from .models import License, LicenseStatus
    warning_date = timezone.now().date() + timedelta(days=30)

    expiring = License.objects.filter(
        status=LicenseStatus.APPROVED,
        expiry_date__lte=warning_date,
        expiry_date__gte=timezone.now().date(),
    ).select_related("project")

    for license in expiring:
        days_left = (license.expiry_date - timezone.now().date()).days
        _send_expiry_alert(license, days_left)

    # Marcar licenças já expiradas
    License.objects.filter(
        status=LicenseStatus.APPROVED,
        expiry_date__lt=timezone.now().date(),
    ).update(status=LicenseStatus.EXPIRED)


def _send_expiry_alert(license, days_left: int):
    # Enviar email/WhatsApp ao gestor do projeto
    subject = f"[ImoOS] Licença expira em {days_left} dias — {license.project.name}"
    pass
```

```python
# settings/celery.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "check-license-expiry": {
        "task": "projects.tasks.check_license_expiry",
        "schedule": crontab(hour=8, minute=0),
    },
}
```

## Key Rules

- Alertar com antecedência de 30, 7 e 1 dia antes do vencimento — registar qual alerta foi enviado para evitar duplicados.
- Atualizar `status=EXPIRED` automaticamente na task diária.
- O campo `document` deve apontar para o S3 com URL assinado de acesso restrito.
- Apenas `MANAGER` e `ADMIN` podem aprovar ou rejeitar licenças.

## Anti-Pattern

```python
# ERRADO: verificar licenças expiradas apenas quando o utilizador abre o projeto
# O sistema deve proativamente alertar via Celery beat, não reativamente
```
