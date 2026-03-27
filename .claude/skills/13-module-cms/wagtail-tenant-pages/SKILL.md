---
name: wagtail-tenant-pages
description: Modelo TenantPage Wagtail com scope por inquilino, blocos StreamField para microsites de projetos e integração de modo de pré-visualização do Next.js.
argument-hint: "[tenant_slug] [page_slug]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Fornecer um CMS baseado em Wagtail onde cada inquilino gere as suas páginas de microsite de projeto. A integração com o modo de pré-visualização do Next.js permite visualizar rascunhos antes de publicar.

## Code Pattern

```python
# cms/models.py
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel

class HeroBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=200)
    subtitle = blocks.TextBlock(required=False)
    background_image = ImageChooserBlock(required=False)
    cta_text = blocks.CharBlock(max_length=100, required=False)
    cta_url = blocks.URLBlock(required=False)

class UnitsGridBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=200, default="As Nossas Unidades")
    project_id = blocks.IntegerBlock(help_text="ID do projeto ImoOS")
    show_available_only = blocks.BooleanBlock(default=True, required=False)

class ContactFormBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=200, default="Contacte-nos")
    project_id = blocks.IntegerBlock()

class TenantPage(Page):
    """Página de microsite de projeto, visível apenas no schema do inquilino."""
    tenant_schema = models.CharField(max_length=63, editable=False)
    body = StreamField([
        ("hero", HeroBlock()),
        ("units_grid", UnitsGridBlock()),
        ("contact_form", ContactFormBlock()),
        ("rich_text", blocks.RichTextBlock()),
        ("map", blocks.StructBlock([
            ("title", blocks.CharBlock()),
            ("project_id", blocks.IntegerBlock()),
        ])),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    def save(self, *args, **kwargs):
        from django_tenants.utils import get_public_schema_name
        from django.db import connection
        self.tenant_schema = connection.schema_name
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Página de Inquilino"
```

```python
# cms/views.py — endpoint para Next.js preview
from django.http import JsonResponse
from wagtail.models import Page

def wagtail_preview_token(request, page_id):
    """GET /cms/preview-token/{page_id}/ — usado pelo Next.js preview mode"""
    if not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)

    import secrets
    token = secrets.token_urlsafe(32)
    from django.core.cache import cache
    cache.set(f"preview_token:{token}", page_id, 300)  # expira em 5 minutos
    return JsonResponse({"token": token, "expires_in": 300})
```

```typescript
// Next.js: pages/api/preview.ts
export default async function handler(req, res) {
  const { token, slug } = req.query;
  const response = await fetch(`${BACKEND_URL}/cms/verify-preview-token/${token}/`);
  if (!response.ok) return res.status(401).json({ message: "Token inválido" });

  res.setPreviewData({ token });
  res.redirect(`/${slug}`);
}
```

## Key Rules

- Filtrar sempre `TenantPage` pelo `tenant_schema` atual — nunca expor páginas de outros inquilinos.
- O bloco `UnitsGridBlock` deve buscar dados de unidades em runtime via API, não no save da página.
- O token de preview expira em 5 minutos — nunca armazenar em base de dados.
- Desativar o Wagtail admin para utilizadores com papel `INVESTOR` — apenas `ADMIN` e `MANAGER`.

## Anti-Pattern

```python
# ERRADO: listar todas as TenantPages sem filtrar por schema
Page.objects.type(TenantPage).all()  # expõe páginas de todos os inquilinos
```
