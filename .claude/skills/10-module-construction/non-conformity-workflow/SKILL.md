---
name: non-conformity-workflow
description: Modelo NonConformity com severity/status (OPEN/IN_PROGRESS/RESOLVED/CLOSED), atribuição de responsável e escalada automática se não resolvido em N dias.
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir não conformidades de qualidade em obra com rastreabilidade completa. A escalada automática garante que problemas críticos não ficam sem resposta, alertando a hierarquia quando o prazo é ultrapassado.

## Code Pattern

```python
# construction/models.py
from django.db import models
from django.utils import timezone

class Severity(models.TextChoices):
    LOW = "LOW", "Baixa"
    MEDIUM = "MEDIUM", "Média"
    HIGH = "HIGH", "Alta"
    CRITICAL = "CRITICAL", "Crítica"

RESOLUTION_DAYS = {
    Severity.LOW: 14,
    Severity.MEDIUM: 7,
    Severity.HIGH: 3,
    Severity.CRITICAL: 1,
}

class NonConformity(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Aberta"
        IN_PROGRESS = "IN_PROGRESS", "Em Resolução"
        RESOLVED = "RESOLVED", "Resolvida"
        CLOSED = "CLOSED", "Fechada"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=Severity.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    responsible = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name="nc_responsible")
    reported_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name="nc_reported")
    opened_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    escalated = models.BooleanField(default=False)
    photo_urls = models.JSONField(default=list)

    def due_date(self):
        days = RESOLUTION_DAYS.get(self.severity, 7)
        return self.opened_at + timezone.timedelta(days=days)

    def is_overdue(self) -> bool:
        return (
            self.status not in [self.Status.RESOLVED, self.Status.CLOSED]
            and timezone.now() > self.due_date()
        )
```

```python
# construction/tasks.py
from celery import shared_task
from django.utils import timezone

@shared_task
def escalate_overdue_non_conformities():
    """Executa diariamente às 07:00."""
    from .models import NonConformity

    for nc in NonConformity.objects.filter(
        status__in=[NonConformity.Status.OPEN, NonConformity.Status.IN_PROGRESS],
        escalated=False,
    ):
        if nc.is_overdue():
            _escalate(nc)


def _escalate(nc: NonConformity):
    from projects.models import ProjectMember, ProjectRole
    managers = ProjectMember.objects.filter(
        project=nc.project, role=ProjectRole.MANAGER
    ).select_related("user")

    for member in managers:
        msg = (
            f"[ESCALADA] Não conformidade '{nc.title}' ({nc.severity}) "
            f"não resolvida em {RESOLUTION_DAYS[nc.severity]} dias no projeto {nc.project.name}."
        )
        # send_email(member.user.email, "NC Escalada", msg)

    nc.escalated = True
    nc.save(update_fields=["escalated"])
```

## Key Rules

- Os prazos de resolução são definidos por `severity` em `RESOLUTION_DAYS` — configurável por inquilino.
- `escalated=True` garante que a escalada ocorre apenas uma vez por não conformidade.
- Apenas `MANAGER` ou `ADMIN` pode fechar (`CLOSED`) uma não conformidade.
- Registar fotos como array de URLs S3 no campo `photo_urls`.

## Anti-Pattern

```python
# ERRADO: escalar sem verificar se já foi escalado
NonConformity.objects.filter(is_overdue=True).update(escalated=True)
# Causa notificações diárias repetidas ao gestor
```
