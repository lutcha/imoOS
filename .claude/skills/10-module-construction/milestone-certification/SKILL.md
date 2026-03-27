---
name: milestone-certification
description: Conclusão de marco requer multi-assinatura (engenheiro + gestor de projeto). Quando todas assinadas: notificar investidores por email/WhatsApp e gerar PDF de certificado.
argument-hint: "[milestone_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Certificar a conclusão de marcos de obra com validação multi-assinatura. O processo garante que tanto o engenheiro responsável como o gestor de projeto validam a conclusão antes de notificar os investidores.

## Code Pattern

```python
# construction/models.py
from django.db import models

class MilestoneCertification(models.Model):
    milestone = models.OneToOneField("projects.Milestone", on_delete=models.CASCADE, related_name="certification")
    certificate_pdf_s3_key = models.CharField(max_length=255, blank=True)
    certified_at = models.DateTimeField(null=True, blank=True)
    investors_notified = models.BooleanField(default=False)


class MilestoneSignature(models.Model):
    class Role(models.TextChoices):
        ENGINEER = "ENGINEER", "Engenheiro"
        MANAGER = "MANAGER", "Gestor de Projeto"

    certification = models.ForeignKey(MilestoneCertification, on_delete=models.CASCADE, related_name="signatures")
    signer = models.ForeignKey("auth.User", on_delete=models.PROTECT)
    role = models.CharField(max_length=20, choices=Role.choices)
    signed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("certification", "role")
```

```python
# construction/services.py
from django.db import transaction
from django.utils import timezone

REQUIRED_ROLES = {"ENGINEER", "MANAGER"}

@transaction.atomic
def sign_milestone_certification(milestone_id: int, user, role: str, notes: str = "") -> dict:
    from .models import MilestoneCertification, MilestoneSignature
    from projects.models import Milestone

    cert, _ = MilestoneCertification.objects.get_or_create(
        milestone_id=milestone_id
    )

    if MilestoneSignature.objects.filter(certification=cert, role=role).exists():
        raise ValueError(f"O papel '{role}' já assinou este marco.")

    MilestoneSignature.objects.create(
        certification=cert, signer=user, role=role, notes=notes
    )

    # Verificar se todas as assinaturas necessárias estão presentes
    signed_roles = set(cert.signatures.values_list("role", flat=True))
    if REQUIRED_ROLES.issubset(signed_roles):
        _complete_certification(cert)

    return {
        "milestone_id": milestone_id,
        "signed_roles": list(signed_roles),
        "missing_roles": list(REQUIRED_ROLES - signed_roles),
        "is_complete": REQUIRED_ROLES.issubset(signed_roles),
    }


def _complete_certification(cert: "MilestoneCertification"):
    from projects.models import Milestone
    from .tasks import generate_certificate_pdf, notify_investors

    cert.certified_at = timezone.now()
    cert.save(update_fields=["certified_at"])

    cert.milestone.status = Milestone.Status.COMPLETED
    cert.milestone.actual_date = timezone.now().date()
    cert.milestone.save(update_fields=["status", "actual_date"])

    generate_certificate_pdf.delay(cert.id)
    notify_investors.delay(milestone_id=cert.milestone_id)
```

```python
# construction/tasks.py
@shared_task
def notify_investors(milestone_id: int):
    from projects.models import Milestone, ProjectMember, ProjectRole
    milestone = Milestone.objects.select_related("project").get(id=milestone_id)
    investors = ProjectMember.objects.filter(
        project=milestone.project, role=ProjectRole.INVESTOR
    ).select_related("user")

    for member in investors:
        msg = f"Marco '{milestone.name}' do projeto {milestone.project.name} foi certificado."
        # send_email(member.user.email, "Marco Certificado", msg)
        # send_whatsapp(member.user.profile.phone, msg)
```

## Key Rules

- Cada papel (`ENGINEER`, `MANAGER`) só pode assinar uma vez por certificação (`unique_together`).
- A certificação só fica completa quando `REQUIRED_ROLES` estão todos assinados.
- A geração do PDF de certificado e a notificação aos investidores são assíncronas via Celery.
- Apenas membros com o papel correto no projeto podem assinar — verificar via `ProjectMember`.

## Anti-Pattern

```python
# ERRADO: completar certificação com apenas uma assinatura
cert.certified_at = timezone.now()
cert.save()  # sem verificar se todas as assinaturas necessárias estão presentes
```
