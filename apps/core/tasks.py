"""
Core Celery tasks for monitoring, alerts, and reports (Sprint 7).
"""
import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.utils import timezone
from django_tenants.utils import schema_context

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def monitor_failed_tasks(self):
    """
    Sprint 7 — Observabilidade.
    
    Monitor Celery task failures and alert super-admins.
    Runs hourly via Celery Beat.
    """
    try:
        from django_celery_results.models import TaskResult
        
        time_threshold = timezone.now() - timezone.timedelta(hours=2)
        
        failed_tasks = (
            TaskResult.objects
            .filter(
                status='FAILURE',
                date_created__gte=time_threshold
            )
            .values('task_name', 'periodic_task_name')
            .annotate(failure_count=Count('id'))
            .order_by('-failure_count')
        )
        
        total_failures = sum(t['failure_count'] for t in failed_tasks)
        
        if total_failures > 5:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin_emails = list(
                User.objects
                .filter(is_staff=True, is_active=True)
                .values_list('email', flat=True)
            )
            
            if not admin_emails:
                return
            
            subject = f"🚨 Alertas de Falhas Celery - {total_failures} falhas nas últimas 2h"
            
            message_lines = [
                f"Total de falhas: {total_failures}",
                f"Período: últimas 2 horas",
                "",
                "Detalhes por task:",
                "-" * 40,
            ]
            
            for task in failed_tasks[:10]:
                task_name = task['task_name'] or task['periodic_task_name'] or 'Unknown'
                count = task['failure_count']
                message_lines.append(f"  • {task_name}: {count} falhas")
            
            message_lines.extend([
                "",
                "Verifique o Flower ou Django Admin para detalhes.",
                "",
                "--",
                "ImoOS Monitoring"
            ])
            
            message = "\n".join(message_lines)
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
            )
            
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=1)
def cleanup_old_task_results(self, days_to_keep=7):
    """
    Cleanup old django_celery_results to prevent DB bloat.
    Runs daily via Celery Beat.
    """
    try:
        from django_celery_results.models import TaskResult
        
        threshold = timezone.now() - timezone.timedelta(days=days_to_keep)
        deleted, _ = TaskResult.objects.filter(date_created__lt=threshold).delete()
        
        return f"Deleted {deleted} old task results"
        
    except Exception as exc:
        raise self.retry(exc=exc)


# ============================================================================
# Report Generation Tasks (Sprint 7 - Prompt 04)
# ============================================================================

@shared_task(bind=True, max_retries=2, default_retry_delay=60, time_limit=300)
def generate_sales_by_project_report(self, report_job_id: str):
    """
    Generate sales by project report (PDF or Excel).
    
    Args:
        report_job_id: UUID of ReportJob instance
    """
    from apps.core.models import ReportJob
    from apps.contracts.models import Contract
    from apps.projects.models import Project
    from django_tenants.utils import schema_context
    
    try:
        report_job = ReportJob.objects.get(id=report_job_id)
    except ReportJob.DoesNotExist:
        logger.error(f'ReportJob {report_job_id} not found')
        return
    
    # Mark as processing
    report_job.mark_processing(progress=10)
    
    try:
        with schema_context(report_job.tenant.schema_name):
            # Get filters
            project_id = report_job.filters.get('project_id')
            start_date = report_job.filters.get('start_date')
            end_date = report_job.filters.get('end_date')
            
            # Build queryset
            contracts = Contract.objects.filter(
                status__in=[Contract.STATUS_ACTIVE, Contract.STATUS_COMPLETED]
            )
            
            if project_id:
                contracts = contracts.filter(project_id=project_id)
            if start_date:
                contracts = contracts.filter(created_at__gte=start_date)
            if end_date:
                contracts = contracts.filter(created_at__lte=end_date)
            
            # Aggregate by project
            report_data = []
            projects = Project.objects.all()
            
            for project in projects:
                project_contracts = contracts.filter(project=project)
                total_cve = project_contracts.aggregate(total=Sum('total_price_cve'))['total'] or 0
                total_eur = project_contracts.aggregate(total=Sum('total_price_eur'))['total'] or 0
                count = project_contracts.count()
                
                report_data.append({
                    'project_name': project.name,
                    'total_units': project.units.count() if hasattr(project, 'units') else 0,
                    'contracts_sold': count,
                    'total_cve': total_cve,
                    'total_eur': total_eur,
                })
            
            report_job.mark_processing(progress=50)
            
            # Generate file based on format
            if report_job.output_format == ReportJob.FORMAT_EXCEL:
                file_url, file_name, file_size = generate_excel_report(
                    report_job, report_data, 'Vendas_por_Projecto'
                )
            elif report_job.output_format == ReportJob.FORMAT_CSV:
                file_url, file_name, file_size = generate_csv_report(
                    report_job, report_data, 'Vendas_por_Projecto'
                )
            else:  # PDF
                file_url, file_name, file_size = generate_pdf_report(
                    report_job, report_data, 'core/reports/sales_by_project.html'
                )
            
            report_job.mark_completed(file_url, file_name, file_size)
            logger.info(f'Report {report_job_id} generated successfully')
            
    except Exception as exc:
        logger.error(f'Failed to generate report {report_job_id}: {exc}', exc_info=True)
        report_job.mark_failed(str(exc))
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=60, time_limit=300)
def generate_crm_pipeline_report(self, report_job_id: str):
    """
    Generate CRM pipeline report (Excel).
    """
    from apps.core.models import ReportJob
    from apps.crm.models import Lead
    from django_tenants.utils import schema_context
    
    try:
        report_job = ReportJob.objects.get(id=report_job_id)
    except ReportJob.DoesNotExist:
        logger.error(f'ReportJob {report_job_id} not found')
        return
    
    report_job.mark_processing(progress=10)
    
    try:
        with schema_context(report_job.tenant.schema_name):
            # Get leads by stage
            leads_by_stage = []
            stages = ['NEW', 'CONTACTED', 'QUALIFIED', 'PROPOSAL', 'NEGOTIATION', 'WON', 'LOST']
            
            for stage in stages:
                count = Lead.objects.filter(stage=stage).count()
                total_budget = Lead.objects.filter(stage=stage).aggregate(
                    total=Sum('budget')
                )['total'] or 0
                
                leads_by_stage.append({
                    'stage': stage,
                    'count': count,
                    'total_budget': total_budget,
                })
            
            report_job.mark_processing(progress=60)
            
            # Generate Excel
            file_url, file_name, file_size = generate_excel_report(
                report_job, leads_by_stage, 'CRM_Pipeline'
            )
            
            report_job.mark_completed(file_url, file_name, file_size)
            
    except Exception as exc:
        logger.error(f'Failed to generate report {report_job_id}: {exc}', exc_info=True)
        report_job.mark_failed(str(exc))
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=60, time_limit=300)
def generate_payment_extract_report(self, report_job_id: str):
    """
    Generate payment extract report (PDF for accounting).
    """
    from apps.core.models import ReportJob
    from apps.payments.models import Payment
    from django_tenants.utils import schema_context
    from django.db.models import Sum
    
    try:
        report_job = ReportJob.objects.get(id=report_job_id)
    except ReportJob.DoesNotExist:
        logger.error(f'ReportJob {report_job_id} not found')
        return
    
    report_job.mark_processing(progress=10)
    
    try:
        with schema_context(report_job.tenant.schema_name):
            filters = report_job.filters
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')
            status = filters.get('status')
            
            payments = Payment.objects.all()
            
            if start_date:
                payments = payments.filter(due_date__gte=start_date)
            if end_date:
                payments = payments.filter(due_date__lte=end_date)
            if status:
                payments = payments.filter(status=status)
            
            # Aggregate data
            report_data = []
            total_paid = 0
            total_pending = 0
            
            for payment in payments.select_related('contract')[:100]:  # Limit 100
                if payment.status == Payment.STATUS_PAID:
                    total_paid += payment.amount_cve or 0
                else:
                    total_pending += payment.amount_cve or 0
                
                report_data.append({
                    'contract': str(payment.contract),
                    'due_date': payment.due_date,
                    'amount_cve': payment.amount_cve,
                    'amount_eur': payment.amount_eur,
                    'status': payment.get_status_display(),
                    'paid_date': payment.paid_date,
                })
            
            report_data.append({
                'contract': 'TOTAL',
                'due_date': '',
                'amount_cve': total_paid + total_pending,
                'amount_eur': 0,
                'status': '',
                'paid_date': f'Pago: {total_paid} | Pendente: {total_pending}',
            })
            
            report_job.mark_processing(progress=60)
            
            # Generate PDF
            file_url, file_name, file_size = generate_pdf_report(
                report_job, report_data, 'core/reports/payment_extract.html'
            )
            
            report_job.mark_completed(file_url, file_name, file_size)
            
    except Exception as exc:
        logger.error(f'Failed to generate report {report_job_id}: {exc}', exc_info=True)
        report_job.mark_failed(str(exc))
        raise self.retry(exc=exc)


# ============================================================================
# Helper Functions
# ============================================================================

def generate_excel_report(report_job, data, prefix='Report'):
    """Generate Excel file and upload to S3."""
    import openpyxl
    from openpyxl import Workbook
    from django.core.files.base import ContentFile
    from apps.tenants.models import Client
    import io
    
    wb = Workbook()
    ws = wb.active
    ws.title = prefix[:31]  # Excel sheet name limit
    
    # Write headers
    if data:
        headers = list(data[0].keys())
        ws.append(headers)
        
        # Write data
        for row in data:
            ws.append([row.get(h) for h in headers])
    
    # Save to buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    # Upload to S3
    file_name = f'{prefix}_{report_job.created_at:%Y%m%d_%H%M%S}.xlsx'
    s3_key = f'tenants/{report_job.tenant.slug}/reports/{file_name}'
    
    import boto3
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL or None,
    )
    
    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=s3_key,
        Body=buffer.getvalue(),
        ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    
    # Generate presigned URL
    file_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': s3_key},
        ExpiresIn=3600 * 24 * 7,  # 7 days
    )
    
    return file_url, file_name, buffer.tell()


def generate_csv_report(report_job, data, prefix='Report'):
    """Generate CSV file and upload to S3."""
    import csv
    import io
    import boto3
    
    buffer = io.StringIO()
    
    if data:
        headers = list(data[0].keys())
        writer = csv.DictWriter(buffer, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
    buffer.seek(0)
    
    file_name = f'{prefix}_{report_job.created_at:%Y%m%d_%H%M%S}.csv'
    s3_key = f'tenants/{report_job.tenant.slug}/reports/{file_name}'
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL or None,
    )
    
    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=s3_key,
        Body=buffer.getvalue().encode('utf-8'),
        ContentType='text/csv',
    )
    
    file_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': s3_key},
        ExpiresIn=3600 * 24 * 7,
    )
    
    return file_url, file_name, len(buffer.getvalue())


def generate_pdf_report(report_job, data, template_name):
    """Generate PDF file using WeasyPrint and upload to S3."""
    from django.template.loader import render_to_string
    from weasyprint import HTML
    import io
    import boto3
    
    # Render template
    html_string = render_to_string(template_name, {
        'report_job': report_job,
        'data': data,
        'tenant': report_job.tenant,
        'generated_at': timezone.now(),
    })
    
    # Generate PDF
    pdf_buffer = io.BytesIO()
    HTML(string=html_string, base_url='.').write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    # Upload to S3
    file_name = f'{report_job.report_type}_{report_job.created_at:%Y%m%d_%H%M%S}.pdf'
    s3_key = f'tenants/{report_job.tenant.slug}/reports/{file_name}'
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL or None,
    )
    
    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=s3_key,
        Body=pdf_buffer.getvalue(),
        ContentType='application/pdf',
    )
    
    file_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': s3_key},
        ExpiresIn=3600 * 24 * 7,
    )
    
    return file_url, file_name, len(pdf_buffer.getvalue())
