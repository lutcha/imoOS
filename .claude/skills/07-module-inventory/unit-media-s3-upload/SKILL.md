---
name: unit-media-s3-upload
description: Geração de URL pré-assinado S3, prefixo por inquilino tenants/{slug}/units/{unit_id}/, compressão de imagem e retorno de URL CDN.
argument-hint: "[unit_id] [content_type]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Permitir upload direto de media de unidades para S3 a partir do cliente, sem passar pelo servidor Django. O backend gera um URL pré-assinado, o cliente faz upload direto e o backend regista a URL CDN.

## Code Pattern

```python
# inventory/views.py
import boto3
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

class UnitMediaPresignedUploadView(APIView):
    """POST /api/v1/inventory/units/{id}/media/presigned-url/"""

    ALLOWED_TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB antes de compressão

    def post(self, request, unit_id):
        content_type = request.data.get("content_type")
        if content_type not in self.ALLOWED_TYPES:
            return Response({"error": "Tipo de ficheiro não permitido."}, status=400)

        ext = self.ALLOWED_TYPES[content_type]
        tenant_slug = request.tenant.schema_name
        file_key = f"tenants/{tenant_slug}/units/{unit_id}/photos/{uuid.uuid4()}.{ext}"

        s3 = boto3.client("s3", region_name=settings.AWS_S3_REGION_NAME)
        presigned = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": file_key,
                "ContentType": content_type,
                "ContentLength": self.MAX_FILE_SIZE,
            },
            ExpiresIn=300,  # 5 minutos
        )

        cdn_url = f"{settings.AWS_S3_CUSTOM_DOMAIN}/{file_key}"
        return Response({
            "upload_url": presigned,
            "cdn_url": cdn_url,
            "key": file_key,
            "expires_in": 300,
        })
```

```python
# inventory/views.py — confirmar upload e registar
class UnitMediaConfirmView(APIView):
    """POST /api/v1/inventory/units/{id}/media/confirm/"""

    def post(self, request, unit_id):
        from .models import UnitMedia
        key = request.data.get("key")
        caption = request.data.get("caption", "")
        order = request.data.get("order", 0)
        cdn_url = f"{settings.AWS_S3_CUSTOM_DOMAIN}/{key}"

        media = UnitMedia.objects.create(
            unit_id=unit_id,
            s3_key=key,
            url=cdn_url,
            caption=caption,
            order=order,
            uploaded_by=request.user,
        )
        return Response({"id": media.id, "url": cdn_url}, status=201)
```

```typescript
// frontend: compressão antes de upload
import imageCompression from "browser-image-compression";

async function uploadUnitPhoto(unitId: number, file: File) {
  const compressed = await imageCompression(file, { maxSizeMB: 1, maxWidthOrHeight: 1920 });
  const { upload_url, cdn_url, key } = await getPresignedUrl(unitId, file.type);
  await fetch(upload_url, { method: "PUT", body: compressed, headers: { "Content-Type": file.type } });
  await confirmUpload(unitId, key);
  return cdn_url;
}
```

## Key Rules

- O prefixo S3 deve seguir sempre `tenants/{slug}/units/{unit_id}/` para isolamento de dados por inquilino.
- A compressão para máximo 1MB deve acontecer no cliente antes do upload — poupar largura de banda e custos S3.
- O URL pré-assinado expira em 5 minutos — não o armazenar nem reutilizar.
- Retornar sempre a URL CDN (não a URL S3 direta) para as listagens.

## Anti-Pattern

```python
# ERRADO: fazer upload de imagem passando pelo servidor Django
def upload_photo(request):
    file = request.FILES["photo"]
    s3.upload_fileobj(file, bucket, key)  # toda a imagem passa pelo servidor — lento e dispendioso
```
