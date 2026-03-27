---
name: landing-page-builder
description: Modelo LandingPage para microsites de projeto com slug/blocks JSON, blocos hero/units-grid/contact-form/map, estados publicado/rascunho.
argument-hint: "[project_id] [slug]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Permitir que cada inquilino crie microsites de projeto com um construtor de páginas baseado em blocos. O sistema de publicação garante que rascunhos não são expostos publicamente.

## Code Pattern

```python
# cms/models.py
from django.db import models

BLOCK_TYPES = ["hero", "units_grid", "contact_form", "map", "rich_text", "gallery", "stats"]

class LandingPage(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Rascunho"
        PUBLISHED = "PUBLISHED", "Publicada"
        ARCHIVED = "ARCHIVED", "Arquivada"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    meta_description = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    blocks = models.JSONField(
        default=list,
        help_text="Lista ordenada de blocos de conteúdo"
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def publish(self, user):
        from django.utils import timezone
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at"])

    @property
    def is_published(self) -> bool:
        return self.status == self.Status.PUBLISHED
```

```python
# cms/serializers.py
from rest_framework import serializers
from .models import LandingPage

VALID_BLOCK_SCHEMA = {
    "hero": {"required": ["title"], "optional": ["subtitle", "background_image_url", "cta_text", "cta_url"]},
    "units_grid": {"required": ["project_id"], "optional": ["show_available_only", "limit"]},
    "contact_form": {"required": ["project_id"], "optional": ["title"]},
    "map": {"required": ["project_id"], "optional": ["title", "zoom"]},
}

class LandingPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPage
        fields = ["id", "slug", "title", "meta_description", "status", "blocks", "published_at"]
        read_only_fields = ["published_at"]

    def validate_blocks(self, blocks):
        if not isinstance(blocks, list):
            raise serializers.ValidationError("blocks deve ser um array.")
        for i, block in enumerate(blocks):
            if "type" not in block:
                raise serializers.ValidationError(f"Bloco {i} sem campo 'type'.")
            if block["type"] not in BLOCK_TYPES:
                raise serializers.ValidationError(f"Tipo de bloco inválido: {block['type']}.")
            schema = VALID_BLOCK_SCHEMA.get(block["type"], {})
            for required_field in schema.get("required", []):
                if required_field not in block:
                    raise serializers.ValidationError(f"Bloco '{block['type']}' requer campo '{required_field}'.")
        return blocks
```

```python
# cms/views.py
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

class LandingPageViewSet(ModelViewSet):
    queryset = LandingPage.objects.all()
    serializer_class = LandingPageSerializer

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        page = self.get_object()
        page.publish(request.user)
        return Response({"status": "published"})
```

## Key Rules

- Apenas páginas com `status=PUBLISHED` são visíveis publicamente — validar no endpoint público.
- Validar o esquema de cada bloco antes de guardar — campos obrigatórios por tipo.
- O `slug` deve ser único por inquilino — usar `unique=True` com scope de schema django-tenants.
- Arquivar (`ARCHIVED`) em vez de eliminar — permite recuperar conteúdo de microsites antigos.

## Anti-Pattern

```python
# ERRADO: expor rascunhos publicamente sem verificar o status
LandingPage.objects.get(slug=slug)  # sem filtrar por status=PUBLISHED
```
