---
name: tenant-branding-config
description: Configuração de marca por inquilino via TenantSettings (logo, cores), serializer de atualização e injeção de variáveis CSS no Next.js.
argument-hint: "[tenant_slug]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Permitir que cada inquilino personalize a interface com o seu logótipo e cor primária. As configurações são guardadas em `TenantSettings` e expostas via API. O frontend Next.js injeta variáveis CSS globais com base na resposta.

## Code Pattern

```python
# tenants/models.py
from django.db import models

class TenantSettings(models.Model):
    plan = models.CharField(max_length=50, default="starter")
    logo_url = models.URLField(blank=True, default="")
    primary_color = models.CharField(max_length=7, default="#1A56DB")  # hex
    company_name = models.CharField(max_length=255, default="")

    class Meta:
        app_label = "tenants"
```

```python
# tenants/serializers.py
from rest_framework import serializers
from .models import TenantSettings

class TenantBrandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantSettings
        fields = ["logo_url", "primary_color", "company_name"]

    def validate_primary_color(self, value):
        if not value.startswith("#") or len(value) != 7:
            raise serializers.ValidationError("Cor deve estar no formato hex (#RRGGBB).")
        return value
```

```python
# tenants/views.py
from rest_framework.generics import RetrieveUpdateAPIView
from .models import TenantSettings
from .serializers import TenantBrandingSerializer

class TenantBrandingView(RetrieveUpdateAPIView):
    serializer_class = TenantBrandingSerializer

    def get_object(self):
        return TenantSettings.objects.get()  # único registo por schema
```

```typescript
// frontend/app/layout.tsx — injeção de variáveis CSS
export default async function RootLayout({ children }) {
  const branding = await fetchBranding(); // GET /api/v1/tenants/branding/
  const style = {
    "--color-primary": branding.primary_color,
  } as React.CSSProperties;

  return (
    <html lang="pt" style={style}>
      <body>{children}</body>
    </html>
  );
}
```

## Key Rules

- `primary_color` deve ser validado como hex de 6 dígitos (`#RRGGBB`) antes de guardar.
- O `logo_url` deve apontar para o CDN do inquilino (prefixo `tenants/{slug}/`), nunca para caminhos locais.
- Apenas utilizadores com papel `ADMIN` podem atualizar as configurações de marca.
- O endpoint de branding deve ser público (sem autenticação) para permitir carregamento no SSR do Next.js.

## Anti-Pattern

```python
# ERRADO: guardar a cor como nome (ex: "blue") em vez de hex — quebra a injeção de CSS
TenantSettings.objects.update(primary_color="blue")
```
