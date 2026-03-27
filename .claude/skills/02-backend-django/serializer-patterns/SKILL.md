---
name: serializer-patterns
description: DRF serializer patterns for ImoOS — nested, writable, CVE/EUR currency validation, read-only computed fields. Auto-load when writing serializers.
argument-hint: [ModelName] [nested-depth]
allowed-tools: Read, Write, Grep
---

# DRF Serializer Patterns — ImoOS

## Standard Model Serializer
```python
# apps/inventory/serializers.py
from rest_framework import serializers
from apps.inventory.models import Unit, UnitPricing

class UnitPricingSerializer(serializers.ModelSerializer):
    final_price_cve = serializers.ReadOnlyField()  # Computed property

    class Meta:
        model = UnitPricing
        fields = ['price_cve', 'price_eur', 'discount_type', 'discount_value', 'final_price_cve']

class UnitSerializer(serializers.ModelSerializer):
    pricing = UnitPricingSerializer(read_only=True)
    project_name = serializers.CharField(source='floor.building.project.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Unit
        fields = ['id', 'code', 'status', 'status_display', 'area_bruta', 'pricing', 'project_name']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UnitCreateSerializer(serializers.ModelSerializer):
    """Used for write operations — stricter validation."""
    class Meta:
        model = Unit
        fields = ['floor', 'unit_type', 'code', 'area_bruta', 'area_util', 'orientation']

    def validate_code(self, value):
        # Code must be unique within the project
        floor = self.initial_data.get('floor')
        if Unit.objects.filter(floor__building=floor, code=value).exists():
            raise serializers.ValidationError(f"Código '{value}' já existe neste edifício.")
        return value.upper()
```

## Writable Nested Serializer
```python
class ProjectWithBuildingsSerializer(serializers.ModelSerializer):
    buildings = BuildingSerializer(many=True, required=False)

    class Meta:
        model = Project
        fields = ['id', 'name', 'status', 'buildings']

    def create(self, validated_data):
        buildings_data = validated_data.pop('buildings', [])
        project = Project.objects.create(**validated_data)
        for b in buildings_data:
            Building.objects.create(project=project, **b)
        return project
```

## Key Rules
- Always use separate Create/Update serializers for write validation
- `read_only_fields` for: id, created_at, updated_at, any computed property
- Validate currency: `price_cve` must be > 0; `price_eur` is derived, not user-editable
- Never expose internal IDs of related tenants in response payloads
