---
name: content-translation-flow
description: Fluxo django-modeltranslation: extrair→traduzir→compilar, rastreio de estado de tradução (DRAFT/TRANSLATED/REVIEWED) e cadeia de fallback pt-PT→pt→en.
argument-hint: "[model_name] [language]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir o ciclo de vida de tradução de conteúdo editorial com rastreabilidade de estado. A cadeia de fallback garante que o utilizador vê sempre conteúdo em vez de campos em branco quando uma tradução não está disponível.

## Code Pattern

```python
# cms/translation.py — registo de campos traduzíveis
from modeltranslation.translator import register, TranslationOptions
from .models import LandingPage, SeoMeta

@register(LandingPage)
class LandingPageTranslation(TranslationOptions):
    fields = ("title", "meta_description")
    # Gera: title_pt, title_pt_pt, title_en

@register(SeoMeta)
class SeoMetaTranslation(TranslationOptions):
    fields = ("title", "description")
```

```python
# cms/models.py — estado de tradução
from django.db import models

class TranslationStatus(models.TextChoices):
    DRAFT = "DRAFT", "Rascunho"
    TRANSLATED = "TRANSLATED", "Traduzido"
    REVIEWED = "REVIEWED", "Revisto"

class ContentTranslationStatus(models.Model):
    """Rastreia o estado de tradução por objeto e idioma."""
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    language = models.CharField(max_length=10)  # ex: "pt-pt", "en"
    status = models.CharField(max_length=20, choices=TranslationStatus.choices, default=TranslationStatus.DRAFT)
    translator = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    translated_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_translations"
    )

    class Meta:
        unique_together = ("content_type", "object_id", "language")
```

```python
# cms/services.py — cadeia de fallback
from django.conf import settings

FALLBACK_CHAIN = ["pt-pt", "pt", "en"]

def get_translated_field(obj, field: str, language: str = None) -> str:
    """
    Obtém o valor traduzido com fallback: pt-PT → pt → en → campo base.
    """
    if language is None:
        from django.utils import translation
        language = translation.get_language() or "pt-pt"

    chain = _build_fallback_chain(language)
    for lang in chain:
        lang_key = lang.replace("-", "_")
        value = getattr(obj, f"{field}_{lang_key}", None)
        if value:
            return value

    return getattr(obj, field, "") or ""  # fallback para o campo base


def _build_fallback_chain(language: str) -> list[str]:
    chain = [language]
    for fallback in FALLBACK_CHAIN:
        if fallback not in chain:
            chain.append(fallback)
    return chain
```

```bash
# Comandos de gestão de traduções
python manage.py makemigrations        # após alterar translation.py
python manage.py update_translation_fields  # preencher campos de tradução existentes
python manage.py compilemessages       # compilar ficheiros .po para .mo
```

## Key Rules

- Usar sempre `get_translated_field()` em vez de `obj.title_pt_pt` diretamente — garante o fallback.
- O estado `REVIEWED` é obrigatório antes de publicar tradução — nunca publicar `DRAFT`.
- A cadeia de fallback é `pt-PT → pt → en` — nunca deixar um campo em branco para o utilizador.
- Correr `makemigrations` após alterar `translation.py` — os campos de idioma são colunas reais na base de dados.

## Anti-Pattern

```python
# ERRADO: aceder diretamente ao campo de idioma sem fallback
title = obj.title_pt_pt  # retorna None se não traduzido — expõe campo vazio ao utilizador
```
