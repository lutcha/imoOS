---
name: photo-geotag-compress
description: React Native com expo-camera, extração de GPS da API de localização, compressão para máx 1MB e upload multipart para /api/v1/construction/photos/ com lat/lon no form data.
argument-hint: "[project_id] [wbs_task_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Permitir o registo fotográfico georreferenciado de progresso de obra a partir de dispositivos móveis. A compressão automática reduz o consumo de dados em zonas de cobertura limitada.

## Code Pattern

```typescript
// mobile/src/features/construction/CapturePhoto.tsx
import { CameraView, useCameraPermissions } from "expo-camera";
import * as Location from "expo-location";
import * as ImageManipulator from "expo-image-manipulator";

interface PhotoUploadParams {
  projectId: number;
  wbsTaskId?: number;
  description?: string;
}

export async function captureAndUploadPhoto(params: PhotoUploadParams): Promise<string> {
  // 1. Capturar foto
  const photo = await cameraRef.current?.takePictureAsync({ quality: 0.9 });
  if (!photo) throw new Error("Falha ao capturar foto.");

  // 2. Obter localização GPS
  const { status } = await Location.requestForegroundPermissionsAsync();
  let lat: number | null = null;
  let lon: number | null = null;
  if (status === "granted") {
    const location = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
    lat = location.coords.latitude;
    lon = location.coords.longitude;
  }

  // 3. Comprimir para máximo 1MB
  const compressed = await ImageManipulator.manipulateAsync(
    photo.uri,
    [{ resize: { width: 1920 } }],
    { compress: 0.75, format: ImageManipulator.SaveFormat.JPEG }
  );

  // Verificar tamanho
  const fileInfo = await FileSystem.getInfoAsync(compressed.uri, { size: true });
  if (fileInfo.size && fileInfo.size > 1024 * 1024) {
    // Segunda passagem com compressão mais agressiva
    const recompressed = await ImageManipulator.manipulateAsync(
      photo.uri,
      [{ resize: { width: 1280 } }],
      { compress: 0.6, format: ImageManipulator.SaveFormat.JPEG }
    );
    return uploadPhoto(recompressed.uri, params, lat, lon);
  }

  return uploadPhoto(compressed.uri, params, lat, lon);
}

async function uploadPhoto(
  uri: string,
  params: PhotoUploadParams,
  lat: number | null,
  lon: number | null
): Promise<string> {
  const formData = new FormData();
  formData.append("photo", { uri, name: "photo.jpg", type: "image/jpeg" } as any);
  formData.append("project_id", String(params.projectId));
  if (params.wbsTaskId) formData.append("wbs_task_id", String(params.wbsTaskId));
  if (lat !== null) formData.append("latitude", String(lat));
  if (lon !== null) formData.append("longitude", String(lon));
  if (params.description) formData.append("description", params.description);

  const response = await fetch(`${API_BASE}/api/v1/construction/photos/`, {
    method: "POST",
    headers: { Authorization: `Bearer ${getToken()}` },
    body: formData,
  });
  const data = await response.json();
  return data.cdn_url;
}
```

```python
# construction/views.py
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser

class ConstructionPhotoUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        photo = request.FILES.get("photo")
        lat = request.data.get("latitude")
        lon = request.data.get("longitude")
        # Fazer upload para S3 e criar registo ConstructionPhoto
        ...
```

## Key Rules

- Pedir permissão de localização antes de tentar obter GPS — não bloquear o upload se a permissão for negada.
- A compressão deve reduzir o ficheiro para menos de 1MB antes de enviar — duas passagens se necessário.
- O `lat/lon` é enviado no form data, não no EXIF — o EXIF pode ser removido por razões de privacidade.
- O backend deve armazenar em S3 com prefixo `tenants/{slug}/construction/photos/` e retornar URL CDN.

## Anti-Pattern

```typescript
// ERRADO: enviar a imagem original sem compressão
formData.append("photo", { uri: photo.uri, ... });  // pode ser 8MB — falha em redes lentas
```
