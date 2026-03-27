---
name: report-generation-pdf
description: Relatório mensal para investidores em PDF: progresso % do projeto, resumo financeiro CVE/EUR, unidades vendidas/disponíveis, próximos marcos. Gerado por Celery beat.
argument-hint: "[project_id] [month] [year]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerar e distribuir automaticamente relatórios mensais aos investidores com uma visão consolidada do progresso e saúde financeira do projeto. O relatório é gerado na última sexta-feira de cada mês.

## Code Pattern

```python
# investors/tasks.py
from celery import shared_task
from celery.schedules import crontab

@shared_task
def generate_monthly_investor_reports():
    """Executa na última sexta-feira do mês às 08:00."""
    from projects.models import Project

    active_projects = Project.objects.filter(is_active=True)
    for project in active_projects:
        generate_project_investor_report.delay(project_id=project.id)


@shared_task(bind=True, max_retries=2)
def generate_project_investor_report(self, project_id: int):
    from django.utils import timezone
    from .services import compile_report_data, render_report_pdf, upload_and_distribute_report

    now = timezone.now()
    report_data = compile_report_data(project_id, month=now.month, year=now.year)
    pdf_bytes = render_report_pdf(report_data)
    upload_and_distribute_report(project_id=project_id, pdf_bytes=pdf_bytes, period=now)
```

```python
# investors/services.py
from decimal import Decimal
from weasyprint import HTML
from django.template.loader import render_to_string

CVE_EUR_RATE = Decimal("110.265")

def compile_report_data(project_id: int, month: int, year: int) -> dict:
    from projects.models import Project, Milestone
    from inventory.models import Unit
    from investors.models import DistributionPayment, Investor

    project = Project.objects.get(id=project_id)
    units = Unit.objects.filter(project=project)

    sold = units.filter(status="SOLD").count()
    available = units.filter(status="AVAILABLE").count()
    reserved = units.filter(status__in=["RESERVED", "CONTRACT"]).count()

    total_revenue_cve = sum(
        u.pricing.price_cve for u in units.filter(status="SOLD").select_related("pricing")
        if hasattr(u, "pricing")
    )

    progress = project.wbs_tasks.aggregate(
        avg=Avg("progress_percentage")
    )["avg"] or Decimal("0")

    next_milestones = Milestone.objects.filter(
        project=project, status="PENDING"
    ).order_by("planned_date")[:3]

    return {
        "project": project,
        "month": month, "year": year,
        "progress_percentage": float(progress),
        "units": {"sold": sold, "available": available, "reserved": reserved, "total": units.count()},
        "revenue_cve": total_revenue_cve,
        "revenue_eur": total_revenue_cve / CVE_EUR_RATE if total_revenue_cve else Decimal("0"),
        "next_milestones": next_milestones,
    }


def render_report_pdf(data: dict) -> bytes:
    html = render_to_string("investors/monthly_report.html", data)
    return HTML(string=html).write_pdf()


def upload_and_distribute_report(project_id, pdf_bytes, period):
    import boto3, uuid
    from django.conf import settings
    from .models import Investor

    key = f"tenants/{get_schema()}/investor_reports/{project_id}/{period.strftime('%Y-%m')}.pdf"
    boto3.client("s3").put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key,
        Body=pdf_bytes, ContentType="application/pdf", ServerSideEncryption="AES256"
    )

    investors = Investor.objects.filter(project_id=project_id, is_active=True).select_related("user")
    for inv in investors:
        send_investor_report_email.delay(investor_id=inv.id, s3_key=key)
```

## Key Rules

- O relatório deve incluir sempre os valores em CVE e EUR (taxa fixa 110.265).
- Gerar um PDF por projeto, não um por investidor — os dados financeiros são os mesmos para todos.
- Armazenar em S3 com encriptação e enviar link pré-assinado (1 semana) por email a cada investidor.
- Usar `Celery beat` com `crontab(day_of_week=4, hour=8, minute=0)` para a última sexta-feira do mês.

## Anti-Pattern

```python
# ERRADO: incluir informação de outros investidores no relatório de um investidor específico
context["all_investors"] = Investor.objects.filter(project=project)  # viola confidencialidade
```
