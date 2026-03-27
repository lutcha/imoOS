---
name: lead-qualification-flow
description: Máquina de estados de Lead: NEW→CONTACTED→QUALIFIED→PROPOSAL→NEGOTIATION→LOST/WON, função score_lead() e atribuição automática a agente disponível.
argument-hint: "[lead_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir o ciclo de vida de um lead no funil de vendas com transições de estado validadas. A pontuação automática ajuda a priorizar leads e a atribuição automática distribui equitativamente pela equipa comercial.

## Code Pattern

```python
# crm/models.py
from django.db import models

class LeadStatus(models.TextChoices):
    NEW = "NEW", "Novo"
    CONTACTED = "CONTACTED", "Contactado"
    QUALIFIED = "QUALIFIED", "Qualificado"
    PROPOSAL = "PROPOSAL", "Proposta Enviada"
    NEGOTIATION = "NEGOTIATION", "Negociação"
    WON = "WON", "Ganho"
    LOST = "LOST", "Perdido"

LEAD_TRANSITIONS = {
    LeadStatus.NEW: [LeadStatus.CONTACTED, LeadStatus.LOST],
    LeadStatus.CONTACTED: [LeadStatus.QUALIFIED, LeadStatus.LOST],
    LeadStatus.QUALIFIED: [LeadStatus.PROPOSAL, LeadStatus.LOST],
    LeadStatus.PROPOSAL: [LeadStatus.NEGOTIATION, LeadStatus.LOST, LeadStatus.WON],
    LeadStatus.NEGOTIATION: [LeadStatus.WON, LeadStatus.LOST],
    LeadStatus.WON: [],
    LeadStatus.LOST: [],
}
```

```python
# crm/services.py
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Lead, LeadStatus, LEAD_TRANSITIONS

User = get_user_model()

def score_lead(lead: Lead) -> int:
    """Pontuação 0-100 com base em completude e comportamento."""
    score = 0
    if lead.email:
        score += 20
    if lead.phone:
        score += 20
    if lead.budget_min and lead.budget_max:
        score += 20
    if lead.preferred_unit_type:
        score += 15
    if lead.utm_source == "REFERRAL":
        score += 25
    return min(score, 100)


def auto_assign_lead(lead: Lead) -> Lead:
    """Atribuir ao agente com menos leads ativos."""
    from django.db.models import Count
    agent = (
        User.objects.filter(profile__role="SALES", is_active=True)
        .annotate(
            active_leads=Count(
                "assigned_leads",
                filter=~models.Q(assigned_leads__status__in=[LeadStatus.WON, LeadStatus.LOST]),
            )
        )
        .order_by("active_leads")
        .first()
    )
    if agent:
        lead.assigned_to = agent
        lead.save(update_fields=["assigned_to"])
    return lead


@transaction.atomic
def advance_lead_status(lead_id: int, new_status: str, user, notes: str = "") -> Lead:
    lead = Lead.objects.select_for_update().get(id=lead_id)
    if new_status not in LEAD_TRANSITIONS.get(lead.status, []):
        from rest_framework.exceptions import ValidationError
        raise ValidationError(f"Transição inválida: {lead.status} → {new_status}")

    lead.status = new_status
    lead.save(update_fields=["status", "updated_at"])
    LeadActivity.objects.create(lead=lead, user=user, action=f"Status: {new_status}", notes=notes)
    return lead
```

## Key Rules

- Toda a progressão de estado deve usar `advance_lead_status()` — nunca atribuição direta.
- `auto_assign_lead()` deve ser chamada em `post_save` quando `status=NEW` e `assigned_to=None`.
- Leads com `score < 30` devem ser marcados como baixa prioridade — não atribuir automaticamente.
- Os estados `WON` e `LOST` são finais — nenhuma transição posterior permitida.

## Anti-Pattern

```python
# ERRADO: saltar etapas do funil para fechar mais rápido
lead.status = "WON"
lead.save()  # salta QUALIFIED e PROPOSAL — perde dados de funil para análise
```
