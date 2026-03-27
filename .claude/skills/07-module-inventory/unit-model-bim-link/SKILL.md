---
name: unit-model-bim-link
description: Campo Unit.bim_guid para ligação a elemento IFC, placeholder para integração de visualizador 3D. O bim_guid é opcional no MVP.
argument-hint: "[unit_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Preparar o modelo `Unit` para futura integração BIM (Building Information Modeling) através do campo `bim_guid` que referencia o elemento IFC correspondente. No MVP este campo é opcional e a visualização 3D é um placeholder.

## Code Pattern

```python
# inventory/models.py
import uuid
from django.db import models

class Unit(models.Model):
    class UnitType(models.TextChoices):
        APARTMENT = "T0", "T0"
        T1 = "T1", "T1"
        T2 = "T2", "T2"
        T3 = "T3", "T3"
        T4 = "T4", "T4"
        COMMERCIAL = "COMMERCIAL", "Comercial"
        PARKING = "PARKING", "Estacionamento"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="units")
    code = models.CharField(max_length=50, unique=True)  # ex: "BL-A-101"
    type = models.CharField(max_length=20, choices=UnitType.choices)
    floor = models.IntegerField(default=0)
    area_bruta = models.DecimalField(max_digits=8, decimal_places=2)
    area_util = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # BIM integration — opcional no MVP
    bim_guid = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        help_text="GUID do elemento IFC no modelo BIM (opcional no MVP)",
        db_index=True,
    )
    bim_ifc_class = models.CharField(
        max_length=100,
        blank=True,
        default="IfcSpace",
        help_text="Classe IFC do elemento, ex: IfcSpace, IfcBuildingStorey",
    )

    def get_bim_viewer_url(self) -> str | None:
        """Placeholder para URL do visualizador 3D — implementar em fase futura."""
        if not self.bim_guid:
            return None
        # TODO: integrar com BIMcollab, Speckle ou viewer proprietário
        return f"/bim/viewer?guid={self.bim_guid}"
```

```python
# inventory/serializers.py
from rest_framework import serializers
from .models import Unit

class UnitSerializer(serializers.ModelSerializer):
    bim_viewer_url = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            "id", "code", "type", "floor",
            "area_bruta", "area_util",
            "bim_guid", "bim_ifc_class", "bim_viewer_url",
        ]

    def get_bim_viewer_url(self, obj):
        return obj.get_bim_viewer_url()
```

## Key Rules

- `bim_guid` é opcional no MVP — nunca tornar obrigatório no formulário de criação de unidade.
- O formato do GUID deve seguir UUID v4 (`xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`).
- Indexar `bim_guid` para permitir lookup rápido quando o visualizador BIM enviar o GUID.
- Documentar claramente que `get_bim_viewer_url()` é um placeholder — não implementar lógica de negócio real neste campo até a fase BIM.

## Anti-Pattern

```python
# ERRADO: tornar bim_guid obrigatório — bloqueia importação de unidades sem modelo BIM
bim_guid = models.UUIDField(unique=True)  # força NOT NULL e quebra o MVP
```
