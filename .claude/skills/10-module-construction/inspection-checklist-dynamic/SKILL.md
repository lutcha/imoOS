---
name: inspection-checklist-dynamic
description: Modelo ChecklistTemplate com campo items JSON, ChecklistInstance criado a partir do template, cada item tem pass/fail/photo/comment e geração de relatório PDF.
argument-hint: "[template_id] [project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir checklists de inspeção de obra dinâmicas. Os templates definem os itens e uma instância é criada para cada inspeção. O relatório PDF consolida todos os resultados com fotos e comentários.

## Code Pattern

```python
# construction/models.py
from django.db import models

class ChecklistTemplate(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)  # ex: "Estrutura", "Elétrico", "Acabamentos"
    items = models.JSONField(
        help_text="""Lista de itens: [{"id": "1", "description": "Verificar prumo das paredes", "required": true}]"""
    )
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)


class ChecklistInstance(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "Em Progresso"
        COMPLETED = "COMPLETED", "Concluído"
        APPROVED = "APPROVED", "Aprovado"

    template = models.ForeignKey(ChecklistTemplate, on_delete=models.PROTECT)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    wbs_task = models.ForeignKey("projects.WBSTask", on_delete=models.SET_NULL, null=True, blank=True)
    inspected_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    inspection_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    results = models.JSONField(default=dict, help_text="Resultados por item_id")
    pdf_s3_key = models.CharField(max_length=255, blank=True)

    def get_pass_rate(self) -> float:
        if not self.results:
            return 0.0
        passed = sum(1 for r in self.results.values() if r.get("result") == "PASS")
        return passed / len(self.results) * 100
```

```python
# construction/services.py
def create_checklist_instance(template_id: int, project_id: int, inspector, date) -> ChecklistInstance:
    template = ChecklistTemplate.objects.get(id=template_id, is_active=True)
    initial_results = {
        item["id"]: {"result": None, "comment": "", "photo_url": None}
        for item in template.items
    }
    return ChecklistInstance.objects.create(
        template=template, project_id=project_id,
        inspected_by=inspector, inspection_date=date,
        results=initial_results,
    )


def record_item_result(instance_id: int, item_id: str, result: str, comment: str = "", photo_url: str = ""):
    """result: 'PASS' | 'FAIL' | 'N/A'"""
    instance = ChecklistInstance.objects.get(id=instance_id)
    if item_id not in instance.results:
        raise ValueError(f"Item '{item_id}' não existe nesta checklist.")
    instance.results[item_id] = {"result": result, "comment": comment, "photo_url": photo_url}
    instance.save(update_fields=["results"])

    # Verificar se todos os itens obrigatórios foram preenchidos
    template_items = {item["id"]: item for item in instance.template.items}
    all_done = all(
        instance.results[item_id]["result"] is not None
        for item_id, item in template_items.items()
        if item.get("required")
    )
    if all_done:
        instance.status = ChecklistInstance.Status.COMPLETED
        instance.save(update_fields=["status"])
```

## Key Rules

- O campo `results` usa o `item_id` do template como chave — nunca o índice (pode mudar entre versões).
- Validar que o `item_id` existe no template antes de registar o resultado.
- Gerar o relatório PDF apenas quando `status=COMPLETED` — incluir pass rate, fotos e comentários.
- Versionamento do template: instâncias mantêm cópia dos `items` do template no momento da criação.

## Anti-Pattern

```python
# ERRADO: guardar resultados como lista ordenada — quebra se o template for atualizado
instance.results = [{"result": "PASS"}, {"result": "FAIL"}]  # sem referência ao item_id
```
