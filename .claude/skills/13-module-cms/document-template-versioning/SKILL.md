---
name: document-template-versioning
description: Modelo DocumentTemplate com version_number/content/is_active, apenas uma versão ativa por tipo, rollback ao definir versão anterior como ativa.
argument-hint: "[template_type]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir versões de templates de documentos (contratos, faturas, propostas) com histórico completo. Apenas uma versão pode estar ativa por tipo, e o rollback é feito simplesmente ativando uma versão anterior.

## Code Pattern

```python
# cms/models.py
from django.db import models

class DocumentTemplateType(models.TextChoices):
    CONTRACT_SALE = "CONTRACT_SALE", "Contrato de Compra e Venda"
    CONTRACT_RESERVATION = "CONTRACT_RESERVATION", "Contrato de Reserva"
    INVOICE = "INVOICE", "Fatura"
    PROPOSAL = "PROPOSAL", "Proposta Comercial"
    CERTIFICATE = "CERTIFICATE", "Certificado de Conclusão"

class DocumentTemplate(models.Model):
    type = models.CharField(max_length=30, choices=DocumentTemplateType.choices)
    version_number = models.PositiveIntegerField()
    content = models.TextField(help_text="HTML com sintaxe Django template")
    changelog = models.TextField(blank=True, help_text="Descrição das alterações desta versão")
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("type", "version_number")
        ordering = ["-version_number"]

    def __str__(self):
        return f"{self.type} v{self.version_number} {'[ATIVA]' if self.is_active else ''}"
```

```python
# cms/services.py
from django.db import transaction
from django.utils import timezone

@transaction.atomic
def activate_document_template(template_id: int, user) -> "DocumentTemplate":
    """Ativa uma versão e desativa todas as outras do mesmo tipo."""
    from .models import DocumentTemplate

    template = DocumentTemplate.objects.select_for_update().get(id=template_id)

    # Desativar versão atual
    DocumentTemplate.objects.filter(
        type=template.type, is_active=True
    ).exclude(id=template_id).update(is_active=False, activated_at=None)

    # Ativar a versão selecionada
    template.is_active = True
    template.activated_at = timezone.now()
    template.save(update_fields=["is_active", "activated_at"])

    # Registar no log de auditoria
    from audit.services import log_action
    log_action(user, "ACTIVATE_TEMPLATE", resource_type="DocumentTemplate",
               resource_id=template_id, details={"type": template.type, "version": template.version_number})

    return template


@transaction.atomic
def create_new_version(type: str, content: str, changelog: str, user) -> "DocumentTemplate":
    """Cria nova versão sem ativar — requer ativação explícita."""
    from .models import DocumentTemplate

    last = DocumentTemplate.objects.filter(type=type).order_by("-version_number").first()
    next_version = (last.version_number + 1) if last else 1

    return DocumentTemplate.objects.create(
        type=type,
        version_number=next_version,
        content=content,
        changelog=changelog,
        is_active=False,
        created_by=user,
    )


def get_active_template(type: str) -> "DocumentTemplate":
    from .models import DocumentTemplate
    try:
        return DocumentTemplate.objects.get(type=type, is_active=True)
    except DocumentTemplate.DoesNotExist:
        raise ValueError(f"Nenhum template ativo para o tipo '{type}'.")
```

## Key Rules

- A ativação de uma versão deve ser uma operação atómica — nunca ter dois templates ativos do mesmo tipo.
- A criação de nova versão não ativa automaticamente — requer ativação explícita por `ADMIN`.
- Manter o histórico completo — nunca eliminar versões antigas, mesmo depois de uma nova estar ativa.
- Documentar o `changelog` ao criar nova versão — é obrigatório para conformidade com auditoria.

## Anti-Pattern

```python
# ERRADO: editar o conteúdo do template existente em vez de criar nova versão
template.content = new_content
template.save()  # perde o histórico — impossível fazer rollback ou auditar alterações
```
