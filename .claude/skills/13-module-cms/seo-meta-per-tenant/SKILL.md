---
name: seo-meta-per-tenant
description: Modelo SeoMeta com page_path/title/description/og_image por inquilino, endpoint para o frontend buscar meta por path e geração automática de sitemap.xml.
argument-hint: "[page_path]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir metadados SEO (título, descrição, Open Graph) por página e por inquilino. O endpoint público permite ao Next.js popular as meta tags no servidor (SSR), e o sitemap é gerado automaticamente.

## Code Pattern

```python
# cms/models.py
from django.db import models

class SeoMeta(models.Model):
    page_path = models.CharField(
        max_length=500,
        help_text="Caminho relativo da página, ex: /projetos/oceano-azul/ ou /unidades/*"
    )
    title = models.CharField(max_length=70, help_text="Máximo 70 caracteres para SEO")
    description = models.CharField(max_length=160, help_text="Máximo 160 caracteres")
    og_image = models.URLField(blank=True, help_text="URL da imagem Open Graph (1200×630px)")
    og_title = models.CharField(max_length=70, blank=True)
    canonical_url = models.URLField(blank=True)
    noindex = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["page_path"]

    def __str__(self):
        return f"{self.page_path}: {self.title}"
```

```python
# cms/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache

class SeoMetaView(APIView):
    """GET /api/v1/cms/seo/?path=/projetos/oceano-azul/ — público, sem autenticação"""
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        path = request.query_params.get("path", "/")
        cache_key = f"seo_meta:{request.tenant.schema_name}:{path}"

        data = cache.get(cache_key)
        if data is None:
            meta = self._find_meta(path)
            data = self._serialize(meta, path) if meta else self._default_meta(path)
            cache.set(cache_key, data, 3600)  # 1 hora

        return Response(data)

    def _find_meta(self, path):
        from .models import SeoMeta
        # Correspondência exata primeiro, depois wildcard
        meta = SeoMeta.objects.filter(page_path=path).first()
        if not meta:
            # Tentar wildcard: /projetos/* corresponde a /projetos/qualquer-coisa/
            parts = path.rstrip("/").split("/")
            for i in range(len(parts), 0, -1):
                wildcard = "/".join(parts[:i]) + "/*"
                meta = SeoMeta.objects.filter(page_path=wildcard).first()
                if meta:
                    break
        return meta

    def _serialize(self, meta, path: str) -> dict:
        from django.conf import settings
        return {
            "title": meta.title,
            "description": meta.description,
            "og_image": meta.og_image or settings.DEFAULT_OG_IMAGE,
            "og_title": meta.og_title or meta.title,
            "canonical_url": meta.canonical_url or f"{settings.FRONTEND_URL}{path}",
            "noindex": meta.noindex,
        }
```

```python
# cms/views.py — sitemap.xml dinâmico
from django.http import HttpResponse

def sitemap_xml(request):
    from .models import SeoMeta, LandingPage
    pages = list(SeoMeta.objects.filter(noindex=False).values("page_path", "updated_at"))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    base = request.build_absolute_uri("/").rstrip("/")
    for page in pages:
        xml.append(f"<url><loc>{base}{page['page_path']}</loc>"
                   f"<lastmod>{page['updated_at'].date().isoformat()}</lastmod></url>")
    xml.append("</urlset>")
    return HttpResponse("\n".join(xml), content_type="application/xml")
```

## Key Rules

- Cachear respostas SEO por 1 hora — os metadados raramente mudam e são consultados em cada page load.
- Invalidar o cache de SEO quando `SeoMeta` é atualizado via sinal `post_save`.
- O campo `title` deve ter no máximo 70 caracteres e `description` 160 — validar no modelo.
- O sitemap deve excluir páginas com `noindex=True`.

## Anti-Pattern

```python
# ERRADO: calcular meta tags no frontend (client-side) — invisível para crawlers de SEO
useEffect(() => { document.title = fetchSeoTitle(); });  // crawlers não executam JavaScript
```
