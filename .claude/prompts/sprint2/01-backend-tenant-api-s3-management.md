# Sprint 2 — Backend: Tenant API + S3 + Management Commands

## Pré-requisito

Bugs do `00-bugfix-criticos-antes-sprint2.md` devem estar corrigidos.
Ler `apps/tenants/models.py` antes de começar — `Client`, `TenantSettings` já existem.

## Estado actual

- `apps/tenants/models.py` — Client, Domain, TenantSettings ✓ (com plan, logo, cores, limites)
- `apps/tenants/middleware.py` — ImoOSTenantMiddleware ✓
- **Falta:** views, serializers, urls, management commands

## Skills a carregar

```
@.claude/skills/05-module-tenants/tenant-onboarding-flow/SKILL.md
@.claude/skills/05-module-tenants/tenant-branding-config/SKILL.md
@.claude/skills/05-module-tenants/tenant-plan-limits/SKILL.md
@.claude/skills/05-module-tenants/tenant-deletion-safe/SKILL.md
@.claude/skills/07-module-inventory/unit-media-s3-upload/SKILL.md
@.claude/skills/02-backend-django/management-commands/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/00-global/security-compliance/SKILL.md
```

## Agents a activar

| Agent | Para que tarefa |
|-------|----------------|
| `model-architect` | Criar `TenantOnboarding` model se necessário, validar estrutura |
| `drf-viewset-builder` | Gerar `TenantSettingsViewSet` com filtros e permissões |
| `tenant-expert` | Auditar views de tenant — garantir que não expõem dados cross-tenant |
| `schema-isolation-auditor` | Verificar que endpoints de settings só afectam o tenant activo |

## Tarefas

### 1. `apps/tenants/serializers.py` — criar

```python
# Ler apps/tenants/models.py primeiro para conhecer todos os campos

class ClientSerializer(serializers.ModelSerializer):
    # Campos públicos da promotora (visíveis no dashboard)
    s3_prefix = serializers.ReadOnlyField()

    class Meta:
        model = Client
        fields = ['id', 'name', 'slug', 'plan', 'country', 'currency',
                  'timezone', 'is_active', 's3_prefix', 'created_at']
        read_only_fields = ['id', 'slug', 'plan', 'created_at']  # plan gerido via billing

class TenantSettingsSerializer(serializers.ModelSerializer):
    # Nunca expor imo_cv_api_key e whatsapp_phone_id em GET público
    # Usar write_only=True para campos sensíveis

    class Meta:
        model = TenantSettings
        fields = ['logo_url', 'primary_color', 'max_projects', 'max_units',
                  'max_users', 'imo_cv_api_key', 'whatsapp_phone_id']
        extra_kwargs = {
            'imo_cv_api_key': {'write_only': True},
            'whatsapp_phone_id': {'write_only': True},
            'max_projects': {'read_only': True},  # gerido pelo plano
            'max_units': {'read_only': True},
            'max_users': {'read_only': True},
        }
```

### 2. `apps/tenants/views.py` — criar

Dois endpoints principais:

**`TenantProfileView`** (GET/PATCH — dados da empresa)
- Retorna `Client` do tenant activo (`request.tenant`)
- PATCH: só `name`, `timezone`, `currency` (não slug, não plan)
- Permission: `IsAuthenticated + IsTenantMember + IsAdminRole`

**`TenantSettingsView`** (GET/PATCH — configurações)
- Retorna/actualiza `TenantSettings` do tenant activo
- PATCH: `logo_url`, `primary_color`, `imo_cv_api_key`, `whatsapp_phone_id`
- Seguir skill `tenant-branding-config` para a lógica de primary_color

**`TenantUsageSummaryView`** (GET — métricas de uso para dashboard)
- Retorna: `{ projects_count, units_count, users_count, plan_limits }`
- Útil para mostrar "X/Y projectos usados" no painel

### 3. `apps/tenants/urls.py` — criar

```python
urlpatterns = [
    path('me/', TenantProfileView.as_view(), name='tenant-profile'),
    path('settings/', TenantSettingsView.as_view(), name='tenant-settings'),
    path('usage/', TenantUsageSummaryView.as_view(), name='tenant-usage'),
]
```

Registar em `config/urls.py`:
```python
path('api/v1/tenant/', include('apps.tenants.urls')),
```

### 4. `apps/tenants/permissions.py` — criar

```python
class IsTenantAdmin(BasePermission):
    """User must be authenticated, in correct tenant, AND have role='admin'."""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.auth and
            request.auth.get('tenant_schema') == connection.schema_name and
            request.user.role == 'admin'
        )
```

### 5. S3 presigned URL endpoint — `apps/inventory/views.py`

Adicionar action ao `UnitViewSet` existente:

```python
@action(detail=True, methods=['post'], url_path='media/upload-url')
def get_upload_url(self, request, pk=None):
    """
    Returns a presigned S3 URL for direct browser upload.
    Frontend uploads directly to S3 — Django never handles the file bytes.
    """
    import boto3, uuid
    from django.conf import settings

    unit = self.get_object()
    tenant_prefix = request.tenant.s3_prefix  # 'tenants/{slug}/'
    file_name = request.data.get('file_name', f'{uuid.uuid4()}.jpg')
    content_type = request.data.get('content_type', 'image/jpeg')

    # Seguir skill unit-media-s3-upload para o padrão completo
    s3 = boto3.client('s3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    key = f'{tenant_prefix}units/{unit.id}/{file_name}'
    presigned_url = s3.generate_presigned_url(
        'put_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': key, 'ContentType': content_type},
        ExpiresIn=300,  # 5 minutos
    )

    return Response({'upload_url': presigned_url, 'key': key})
```

### 6. Management command `create_tenant`

**`apps/tenants/management/commands/create_tenant.py`**

```
python manage.py create_tenant \
  --schema=empresa_abc \
  --name="Empresa ABC Lda" \
  --domain=empresa-abc.imos.cv \
  --plan=starter \
  --admin-email=admin@empresa-abc.cv \
  --admin-password=changeme123
```

O comando deve:
1. Criar `Client` (auto_create_schema=True cria o schema PostgreSQL)
2. Criar `Domain` ligado ao Client
3. Criar `TenantSettings` com defaults
4. Dentro de `tenant_context()`: criar o User admin inicial
5. Confirmar no terminal: "✅ Tenant empresa_abc criado. Schema: empresa_abc. Admin: admin@empresa-abc.cv"

Seguir skill `management-commands` para estrutura base.
Seguir skill `tenant-onboarding-flow` para a sequência correcta.

### 7. `apps/tenants/management/commands/tenant_stats.py`

```
python manage.py tenant_stats  # lista todos os tenants com projectos/unidades/users count
```

Útil para operações — mostra tabela de todos os tenants activos.

## Verificação final

- [ ] `GET /api/v1/tenant/me/` retorna nome e plano do tenant activo
- [ ] `PATCH /api/v1/tenant/settings/` actualiza `logo_url` e `primary_color`
- [ ] `POST /api/v1/inventory/units/{id}/media/upload-url/` retorna presigned URL válido
- [ ] `python manage.py create_tenant --schema=test --name="Test" --domain=test.imos.cv --admin-email=a@a.cv --admin-password=pass123` cria schema
- [ ] `python manage.py tenant_stats` lista tenants sem erro
- [ ] `IsTenantAdmin`: user com role='gestor' recebe 403 em endpoints de admin
