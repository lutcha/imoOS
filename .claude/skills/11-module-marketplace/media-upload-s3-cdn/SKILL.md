---
name: media-upload-s3-cdn
description: Upload para S3 com prefixo por inquilino, geração de URL CDN e sincronização de URLs de imagem para o listing do imo.cv via chamada de atualização à API.
argument-hint: "[unit_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir o ciclo de vida de media de unidades: upload para S3 com prefixo por inquilino, exposição via CDN e sincronização das URLs com o portal imo.cv para manter as imagens atualizadas nos dois sistemas.

## Code Pattern

```python
# marketplace/tasks.py
from celery import shared_task
import requests
from django.conf import settings

@shared_task(bind=True, max_retries=3, retry_backoff=True)
def sync_unit_images_to_marketplace(self, unit_id: int):
    """Sincroniza URLs de imagens do S3/CDN para o listing do imo.cv."""
    from inventory.models import Unit

    unit = Unit.objects.prefetch_related("media").get(id=unit_id)
    if not unit.external_listing_id:
        return {"skipped": True, "reason": "Sem listing externo"}

    # Ordenar por campo order e pegar as primeiras 20
    cdn_urls = list(
        unit.media.order_by("order").values_list("url", flat=True)[:20]
    )

    response = requests.patch(
        f"{settings.IMO_CV_API_URL}/listings/{unit.external_listing_id}/",
        json={"images": cdn_urls},
        headers={"Authorization": f"Bearer {settings.IMO_CV_API_TOKEN}"},
        timeout=15,
    )
    response.raise_for_status()
    return {"unit_id": unit_id, "images_synced": len(cdn_urls)}
```

```python
# inventory/signals.py — disparar sync após novo upload de media
from django.db.models.signals import post_save
from django.dispatch import receiver
from inventory.models import UnitMedia

@receiver(post_save, sender=UnitMedia)
def trigger_marketplace_image_sync(sender, instance, created, **kwargs):
    if created and instance.unit.external_listing_id:
        from marketplace.tasks import sync_unit_images_to_marketplace
        # Atrasar 5 segundos para agrupar uploads em lote
        sync_unit_images_to_marketplace.apply_async(
            args=[instance.unit_id], countdown=5
        )
```

```python
# inventory/models.py — gestão de ordenação de media
class UnitMedia(models.Model):
    unit = models.ForeignKey("Unit", on_delete=models.CASCADE, related_name="media")
    s3_key = models.CharField(max_length=500)
    url = models.URLField(max_length=500)  # URL CDN
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_cover = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]
        indexes = [models.Index(fields=["unit", "order"])]
```

```python
# Função utilitária para geração de URL CDN
def get_cdn_url(s3_key: str) -> str:
    """Converte s3_key em URL CDN — evitar URLs S3 diretas nas listagens."""
    return f"https://{settings.CDN_DOMAIN}/{s3_key}"
```

## Key Rules

- Usar sempre URL CDN (não URL S3 direta) nas listagens do imo.cv — performance e custos.
- O `countdown=5` no sinal agrupa múltiplos uploads em lote evitando chamadas redundantes à API.
- Limitar a 20 imagens por listing (limite do imo.cv) — ordenar por `order` e cortar o excedente.
- A imagem de capa (`is_cover=True`) deve sempre ser a primeira no array enviado ao imo.cv.

## Anti-Pattern

```python
# ERRADO: sincronizar imagem por imagem em vez de em lote
@receiver(post_save, sender=UnitMedia)
def sync_one_image(sender, instance, **kwargs):
    requests.patch(IMO_CV_URL, json={"images": [instance.url]})  # substitui todas as imagens anteriores
```
