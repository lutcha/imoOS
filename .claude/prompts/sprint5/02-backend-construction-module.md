# Sprint 5 — Backend: Módulo de Obra (`apps/construction`)

## Contexto

`apps/construction/` existe como directório vazio. O módulo de obra é crítico para
o caso de uso offline-first da app móvel em Cabo Verde — os engenheiros de obra
registam relatórios diários e fotos em campo, sem ligação estável à internet.

## Pré-requisitos — Ler antes de começar

```
apps/construction/          → verificar estado actual (esperado: vazio ou __init__.py)
apps/projects/models.py     → Project, Building, Floor — FKs a usar
apps/core/models.py         → TenantAwareModel — herdar daqui
apps/users/permissions.py   → IsTenantMember — base das permissions
apps/memberships/models.py  → roles: engenheiro, admin, gestor
config/settings/base.py     → TENANT_APPS — adicionar apps.construction
```

```bash
ls apps/construction/
grep "TENANT_APPS" config/settings/base.py
```

## Skills a carregar

```
@.claude/skills/11-module-construction/daily-report/SKILL.md
@.claude/skills/11-module-construction/photo-geotagged/SKILL.md
@.claude/skills/02-backend-django/model-audit-history/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
```

## Agents a activar (por esta ordem)

| Agent | Tarefa |
|-------|--------|
| `model-architect` | Modelos DailyReport, Photo, ConstructionProgress |
| `drf-viewset-builder` | ViewSets + serializers + filtros |
| `celery-task-specialist` | Task: processar e optimizar fotos (thumbnail + S3) |
| `isolation-test-writer` | Testes de isolamento do módulo de obra |

---

## Tarefa 1 — Modelos (`apps/construction/models.py`)

Prompt para `model-architect`:
> "Cria os modelos do módulo de obra para ImoOS. `DailyReport`: FK para `Project`, `Building` (opcional), data, autor (User), resumo do dia, percentagem de progresso (0-100), status (DRAFT/SUBMITTED/APPROVED), HistoricalRecords. `ConstructionPhoto`: FK para `DailyReport`, ficheiro S3 (CharField com key), caption, latitude/longitude (DecimalField nullable — geotag), thumbnail_s3_key, created_by. `ConstructionProgress`: OneToOne com `Building`, percentagem global, última actualização. Todos herdam TenantAwareModel."

```python
# Estrutura esperada

class DailyReport(TenantAwareModel):
    STATUS_DRAFT = 'DRAFT'
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_APPROVED = 'APPROVED'

    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    building = models.ForeignKey('projects.Building', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    summary = models.TextField()
    progress_pct = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentagem de obra concluída na data deste relatório',
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    weather = models.CharField(max_length=50, blank=True)
    workers_count = models.PositiveSmallIntegerField(default=0)
    history = HistoricalRecords()

    class Meta:
        unique_together = [('project', 'building', 'date')]
        ordering = ['-date']


class ConstructionPhoto(TenantAwareModel):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='photos')
    s3_key = models.CharField(max_length=500)
    thumbnail_s3_key = models.CharField(max_length=500, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    @property
    def has_geotag(self) -> bool:
        return self.latitude is not None and self.longitude is not None
```

---

## Tarefa 2 — ViewSets (`apps/construction/views.py`)

Prompt para `drf-viewset-builder`:
> "Gera `DailyReportViewSet` e `ConstructionPhotoViewSet` para ImoOS. `DailyReportViewSet`: leitura para IsTenantMember, escrita para roles engenheiro/admin. Action `submit` (DRAFT→SUBMITTED), action `approve` (SUBMITTED→APPROVED, apenas admin). Filtros por project, building, date_range, status. `ConstructionPhotoViewSet`: CRUD ligado a um report. Serializer inclui URL presignada de leitura para s3_key e thumbnail_s3_key."

**Permission personalizada para engenheiros:**
```python
class IsEngineerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        from apps.memberships.models import TenantMembership
        try:
            m = TenantMembership.objects.get(user=request.user)
            return m.role in ('admin', 'gestor', 'engenheiro')
        except TenantMembership.DoesNotExist:
            return False
```

---

## Tarefa 3 — Celery task: processar fotos

Prompt para `celery-task-specialist`:
> "Cria `apps/construction/tasks.py` com `process_construction_photo`. Recebe `tenant_schema` e `photo_id`. Dentro de `tenant_context`: fetch a photo, descarrega o S3 original, cria thumbnail 800×600 com Pillow, faz upload do thumbnail para S3 com key `{original_key}_thumb.jpg`, actualiza `photo.thumbnail_s3_key`. Retry ×3 com backoff. A task é idempotente — se thumbnail já existe, faz skip."

---

## Tarefa 4 — URLs e registos

`apps/construction/urls.py`:
```python
router.register(r'daily-reports', DailyReportViewSet, basename='daily-report')
router.register(r'photos', ConstructionPhotoViewSet, basename='construction-photo')
```

`config/urls.py` — adicionar:
```python
path('api/v1/construction/', include('apps.construction.urls')),
```

`config/settings/base.py` — adicionar a `TENANT_APPS`:
```python
'apps.construction',
```

---

## Tarefa 5 — Testes de isolamento

Prompt para `isolation-test-writer`:
> "Escreve `tests/tenant_isolation/test_construction_isolation.py`. Verificar: (1) relatório de tenant_a não visível em tenant_b, (2) submit/approve num relatório de outro tenant → 404, (3) fotos isoladas por schema, (4) progress_pct não vaza entre tenants."

---

## Verificação final

- [ ] `python manage.py check` sem erros
- [ ] `python manage.py migrate_schemas` cria tabelas correctas
- [ ] `POST /api/v1/construction/daily-reports/` → 201
- [ ] `POST /api/v1/construction/daily-reports/{id}/submit/` → status=SUBMITTED
- [ ] `POST /api/v1/construction/daily-reports/{id}/approve/` → status=APPROVED (admin only)
- [ ] `pytest tests/tenant_isolation/test_construction_isolation.py -v`
