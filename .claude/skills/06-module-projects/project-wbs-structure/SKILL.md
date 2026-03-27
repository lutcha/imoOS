---
name: project-wbs-structure
description: Modelo WBS com FK para pai (lista de adjacência), campo progress_percentage e cálculo de rollup via query recursiva.
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Modelar a estrutura analítica de trabalho (WBS) de um projeto com hierarquia ilimitada. O progresso de nós pai é calculado automaticamente como média ponderada dos filhos via query recursiva PostgreSQL.

## Code Pattern

```python
# projects/models.py
from django.db import models

class WBSTask(models.Model):
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="wbs_tasks")
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.CASCADE, related_name="children"
    )
    code = models.CharField(max_length=50)        # ex: "1.2.3"
    name = models.CharField(max_length=255)
    progress_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    planned_start = models.DateField(null=True, blank=True)
    planned_end = models.DateField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1)

    class Meta:
        ordering = ["code"]
```

```python
# projects/services.py
from django.db import connection

def rollup_wbs_progress(project_id: int) -> None:
    """Atualiza progress_percentage de todos os nós via CTE recursiva."""
    sql = """
    WITH RECURSIVE wbs_tree AS (
        -- Nós folha: progresso direto
        SELECT id, parent_id, progress_percentage, weight
        FROM projects_wbstask
        WHERE project_id = %s

        UNION ALL

        SELECT p.id, p.parent_id,
               (SELECT SUM(c.progress_percentage * c.weight) / NULLIF(SUM(c.weight), 0)
                FROM projects_wbstask c WHERE c.parent_id = p.id),
               p.weight
        FROM projects_wbstask p
        INNER JOIN wbs_tree t ON t.parent_id = p.id
    )
    UPDATE projects_wbstask wbs
    SET progress_percentage = COALESCE(tree.progress_percentage, 0)
    FROM (
        SELECT id, AVG(progress_percentage) as progress_percentage
        FROM wbs_tree GROUP BY id
    ) tree
    WHERE wbs.id = tree.id AND wbs.project_id = %s;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [project_id, project_id])
```

```python
# projects/serializers.py
from rest_framework import serializers
from .models import WBSTask

class WBSTaskSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = WBSTask
        fields = ["id", "code", "name", "progress_percentage", "weight", "children"]

    def get_children(self, obj):
        return WBSTaskSerializer(obj.children.all(), many=True).data
```

## Key Rules

- Chamar `rollup_wbs_progress()` após cada atualização de progresso num nó folha.
- Os nós folha (sem filhos) têm `progress_percentage` definido manualmente; os nós pai são calculados.
- Usar `weight` para calcular média ponderada em vez de média simples.
- Limitar a profundidade máxima da WBS a 6 níveis para evitar queries lentas.

## Anti-Pattern

```python
# ERRADO: calcular rollup em Python com múltiplas queries
for task in WBSTask.objects.filter(parent=None):
    children = task.children.all()  # N+1 queries
    task.progress_percentage = sum(c.progress_percentage for c in children) / len(children)
    task.save()
```
