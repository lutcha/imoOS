# Sprint 7 — Relatórios e Exportações

## Contexto

As promotoras precisam de exportar dados para uso externo:
1. **Relatório de vendas por projecto** (PDF + Excel)
2. **Pipeline CRM** (Excel — para análise em sheets)
3. **Extracto de pagamentos** (PDF — para contabilidade)
4. **Relatório de obra** (PDF — para clientes e investidores)

A geração é **assíncrona** (Celery) — relatórios grandes não bloqueiam requests.
O frontend mostra o estado da geração e link de download quando pronto (S3 presigned URL).

## Pré-requisitos — Ler antes de começar

```
apps/contracts/tasks.py         → generate_contract_pdf (padrão WeasyPrint + S3)
apps/inventory/models.py        → Unit, UnitPricing
apps/crm/models.py              → Lead, Interaction
apps/construction/models.py     → DailyReport, Progress
apps/payments/models.py         → Payment, PaymentPlan
config/settings/base.py         → AWS_* (S3)
```

```bash
cat apps/contracts/tasks.py | head -60  # ver padrão WeasyPrint
grep "WeasyPrint\|weasyprint\|openpyxl" requirements/base.txt
```

## Skills a carregar

```
@.claude/skills/03-async-celery/celery-safe-pattern/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/02-backend-django/model-audit-history/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `model-architect` | ReportJob model (rastreia estado das gerações) |
| `celery-task-specialist` | Tasks de geração (PDF/Excel) por tipo de relatório |
| `drf-viewset-builder` | ReportJobViewSet — criar job + polling de estado + download |
| `react-component-builder` | Páginas de relatório com botão "Gerar" + estado de polling |

---

## Tarefa 1 — Modelo ReportJob

Prompt para `model-architect`:
> "Cria `ReportJob` em `apps/core/models.py` (ou app dedicada `apps/reports/`). Campos: `report_type` (SALES_BY_PROJECT/CRM_PIPELINE/PAYMENT_EXTRACT/CONSTRUCTION_REPORT), `format` (PDF/EXCEL), `parameters` (JSONField — ex: {project_id: ..., date_from: ...}), `status` (PENDING/RUNNING/DONE/FAILED), `s3_key` (CharField, blank), `error` (TextField), `requested_by` (FK User), `created_at`, `completed_at`. TenantAwareModel + sem HistoricalRecords (é um job log)."

```python
class ReportJob(TenantAwareModel):
    TYPE_SALES        = 'SALES_BY_PROJECT'
    TYPE_CRM          = 'CRM_PIPELINE'
    TYPE_PAYMENTS     = 'PAYMENT_EXTRACT'
    TYPE_CONSTRUCTION = 'CONSTRUCTION_REPORT'

    FORMAT_PDF   = 'PDF'
    FORMAT_EXCEL = 'EXCEL'

    report_type  = models.CharField(max_length=25, choices=TYPE_CHOICES)
    format       = models.CharField(max_length=5, choices=FORMAT_CHOICES, default=FORMAT_PDF)
    parameters   = models.JSONField(default=dict)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    s3_key       = models.CharField(max_length=500, blank=True)
    error        = models.TextField(blank=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    @property
    def download_url(self) -> str | None:
        """Presigned S3 URL válida por 1 hora."""
        if self.status != 'DONE' or not self.s3_key:
            return None
        import boto3
        from django.conf import settings as django_settings
        s3 = boto3.client('s3', endpoint_url=django_settings.AWS_S3_ENDPOINT_URL)
        return s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': django_settings.AWS_STORAGE_BUCKET_NAME, 'Key': self.s3_key},
            ExpiresIn=3600,
        )
```

---

## Tarefa 2 — Tasks de geração de relatórios

Prompt para `celery-task-specialist`:
> "Cria `generate_report(tenant_schema, job_id)` em `apps/core/tasks.py` (ou `apps/reports/tasks.py`). Dentro de `tenant_context`: (1) carrega ReportJob, marca RUNNING, (2) despachea para sub-função baseada em `job.report_type` + `job.format`, (3) faz upload S3, (4) actualiza `job.s3_key`, `job.status=DONE`, `job.completed_at`. Em erro: `job.status=FAILED`, `job.error=str(e)`. Timeout=300s. Não retry (relatórios são gerados sob pedido).

Sub-funções a criar:
- `_generate_sales_pdf(job)` → WeasyPrint, tabela de unidades vendidas por projecto
- `_generate_sales_excel(job)` → openpyxl, folhas: Resumo | Por Projecto | Por Unidade
- `_generate_crm_excel(job)` → leads + interacções + estágio
- `_generate_payments_pdf(job)` → extracto de pagamentos recebidos por período"

**Instalar**: `openpyxl==3.1.2` em `requirements/base.txt` (WeasyPrint já existe).

---

## Tarefa 3 — ReportJobViewSet

Prompt para `drf-viewset-builder`:
> "Cria `ReportJobViewSet` em `apps/core/views.py`. Permission: IsTenantMember. Actions: `create` (cria job + enfileira task), `retrieve` (polling de estado), `download` (retorna {download_url} com presigned URL S3). Filtro: user vê apenas os seus jobs (a menos que role=admin). Limite: 1 job activo por type+format por utilizador (PENDING ou RUNNING)."

```python
# POST /api/v1/reports/jobs/
# Body: {report_type: "SALES_BY_PROJECT", format: "PDF", parameters: {project_id: "..."}}
# Response: {id: "...", status: "PENDING", created_at: "..."}

# GET /api/v1/reports/jobs/{id}/
# Response: {id, status, report_type, format, created_at, completed_at, download_url (null se PENDING)}

# GET /api/v1/reports/jobs/{id}/download/
# Response: {download_url: "https://s3.../..."} ou 404 se não DONE
```

---

## Tarefa 4 — Templates de relatório

### Relatório de Vendas (HTML para WeasyPrint)

Criar `apps/core/templates/reports/sales_by_project.html`:
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: 'Helvetica Neue', sans-serif; font-size: 11px; }
    .header { border-bottom: 2px solid #2563eb; padding-bottom: 10px; margin-bottom: 20px; }
    .logo { height: 32px; }
    table { width: 100%; border-collapse: collapse; }
    th { background: #2563eb; color: white; padding: 6px 8px; text-align: left; }
    td { padding: 5px 8px; border-bottom: 1px solid #e5e7eb; }
    .total { font-weight: bold; background: #f9fafb; }
    .badge-available { color: #16a34a; }
    .badge-sold { color: #2563eb; }
    .badge-reserved { color: #d97706; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Relatório de Vendas — {{ tenant_name }}</h1>
    <p>Período: {{ date_from }} a {{ date_to }} | Gerado em: {{ generated_at }}</p>
  </div>
  {% for project in projects %}
  <h2>{{ project.name }} — {{ project.city }}, {{ project.island }}</h2>
  <table>
    <tr><th>Unidade</th><th>Tipologia</th><th>Estado</th><th>Preço CVE</th><th>Data Venda</th></tr>
    {% for unit in project.units %}
    <tr>
      <td>{{ unit.code }}</td>
      <td>{{ unit.typology }}</td>
      <td class="badge-{{ unit.status|lower }}">{{ unit.status_display }}</td>
      <td>{{ unit.price_cve|intcomma }}</td>
      <td>{{ unit.sold_at|default:"-" }}</td>
    </tr>
    {% endfor %}
    <tr class="total">
      <td colspan="3">Total Vendido</td>
      <td>{{ project.total_sold_cve|intcomma }}</td>
      <td></td>
    </tr>
  </table>
  {% endfor %}
</body>
</html>
```

---

## Tarefa 5 — Frontend: /reports/

Criar `frontend/src/app/reports/page.tsx`:
```typescript
// 4 cards de tipo de relatório:
// [📊 Vendas por Projecto] [👥 Pipeline CRM] [💰 Extracto Pagamentos] [🏗️ Relatório de Obra]
// Cada card tem:
//   - Descrição breve
//   - Select de formato (PDF / Excel)
//   - Campos de parâmetros (ex: projecto, período)
//   - Botão "Gerar Relatório"
//   - Estado do job: PENDING (spinner) → RUNNING (spinner) → DONE (link Download) → FAILED (erro)
// Polling automático a cada 3s enquanto status = PENDING/RUNNING
```

```typescript
// Hook de polling:
function useReportJobStatus(jobId: string | null) {
  return useQuery({
    queryKey: ['report-job', jobId],
    queryFn: () => api.get(`/reports/jobs/${jobId}/`),
    enabled: !!jobId,
    refetchInterval: (data) =>
      data?.status === 'DONE' || data?.status === 'FAILED' ? false : 3000,
  });
}
```

---

## Verificação final

- [ ] `POST /api/v1/reports/jobs/` → cria job, task enfileirada
- [ ] `GET /api/v1/reports/jobs/{id}/` → status actualizado (PENDING→RUNNING→DONE)
- [ ] `GET /api/v1/reports/jobs/{id}/download/` → `download_url` válida por 1h
- [ ] PDF de vendas gerado com dados reais do tenant
- [ ] Excel CRM tem colunas: Nome, Email, Telefone, Estágio, Fonte, Data
- [ ] Tenant A não acede a relatórios de Tenant B
- [ ] Polling no frontend para quando DONE → link aparece automaticamente
- [ ] Erro de geração → badge FAILED + mensagem no frontend
