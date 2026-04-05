"""
Construction Celery tasks.

Tarefas agendadas:
- daily_reminders: Lembretes diários de tasks (8h)
- check_overdue: Verificar tasks atrasadas (9h)
- recalculate_cpm: Recalcular CPM diariamente
- evm_snapshot: Snapshot diário EVM
"""
import logging

from celery import shared_task
from django.utils import timezone

from .models import ConstructionTask
from .services import CPMCalculator, EVMCalculator
from .signals import send_daily_reminders, check_overdue_tasks

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_daily_task_reminders(self):
    """
    Enviar lembretes diários para tasks do dia.
    
    Schedule: Todo dia às 8h (configurar no Django Admin > Periodic Tasks)
    """
    logger.info('Iniciando envio de lembretes diários...')
    
    try:
        send_daily_reminders()
        logger.info('Lembretes diários enviados com sucesso.')
        return {'status': 'success', 'message': 'Lembretes enviados'}
    except Exception as exc:
        logger.error(f'Erro ao enviar lembretes: {exc}')
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=3)
def check_overdue_tasks_task(self):
    """
    Verificar tasks atrasadas e notificar.
    
    Schedule: Todo dia às 9h
    """
    logger.info('Verificando tasks atrasadas...')
    
    try:
        check_overdue_tasks()
        logger.info('Verificação de atrasos concluída.')
        return {'status': 'success', 'message': 'Atrasos verificados'}
    except Exception as exc:
        logger.error(f'Erro ao verificar atrasos: {exc}')
        raise self.retry(exc=exc, countdown=300)


@shared_task
def recalculate_project_cpm(project_id: str):
    """
    Recalcular CPM para um projeto.
    
    Chamado automaticamente quando:
    - Tasks são criadas/alteradas
    - Dependências são alteradas
    """
    logger.info(f'Recalculando CPM para projeto {project_id}...')
    
    try:
        calculator = CPMCalculator(project_id)
        stats = calculator.recalculate_project()
        
        logger.info(f'CPM recalculado: {stats}')
        return {
            'status': 'success',
            'project_id': project_id,
            'stats': stats
        }
    except Exception as exc:
        logger.error(f'Erro ao recalcular CPM: {exc}')
        return {
            'status': 'error',
            'project_id': project_id,
            'error': str(exc)
        }


@shared_task
def generate_evm_snapshot(project_id: str):
    """
    Gerar snapshot EVM diário para um projeto.
    
    Schedule: Todo dia às 18h (fim do dia de trabalho)
    """
    logger.info(f'Gerando snapshot EVM para projeto {project_id}...')
    
    try:
        calculator = EVMCalculator(project_id)
        data = calculator.calculate(as_of_date=timezone.now().date(), save_snapshot=True)
        
        logger.info(f'Snapshot EVM gerado: SPI={data["spi"]}, CPI={data["cpi"]}')
        return {
            'status': 'success',
            'project_id': project_id,
            'spi': float(data['spi']),
            'cpi': float(data['cpi'])
        }
    except Exception as exc:
        logger.error(f'Erro ao gerar snapshot EVM: {exc}')
        return {
            'status': 'error',
            'project_id': project_id,
            'error': str(exc)
        }


@shared_task
def generate_all_evm_snapshots():
    """
    Gerar snapshots EVM para todos os projetos ativos.
    
    Schedule: Todo dia às 18h
    """
    from apps.projects.models import Project
    
    active_projects = Project.objects.filter(
        status=Project.STATUS_CONSTRUCTION
    ).values_list('id', flat=True)
    
    results = []
    for project_id in active_projects:
        result = generate_evm_snapshot.delay(str(project_id))
        results.append(str(project_id))
    
    logger.info(f'Snapshots EVM agendados para {len(results)} projetos')
    return {
        'status': 'success',
        'projects': results
    }


@shared_task
def update_phase_progress(phase_id: str):
    """
    Atualizar progresso agregado de uma fase.
    
    Chamado automaticamente quando tasks são alteradas.
    """
    from .models import ConstructionPhase
    
    try:
        phase = ConstructionPhase.objects.get(id=phase_id)
        phase.recalculate_progress()
        
        logger.info(f'Progresso da fase {phase.name} atualizado: {phase.progress_percent}%')
        return {
            'status': 'success',
            'phase_id': phase_id,
            'progress': float(phase.progress_percent)
        }
    except ConstructionPhase.DoesNotExist:
        return {
            'status': 'error',
            'phase_id': phase_id,
            'error': 'Fase não encontrada'
        }
    except Exception as exc:
        logger.error(f'Erro ao atualizar progresso da fase: {exc}')
        return {
            'status': 'error',
            'phase_id': phase_id,
            'error': str(exc)
        }


@shared_task
def cleanup_old_notifications(days: int = 30):
    """
    Limpar flags de notificação antigas para permitir reenvio.
    
    Schedule: Mensalmente
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    
    # Resetar reminder_sent para tasks pendentes
    updated = ConstructionTask.objects.filter(
        reminder_sent=True,
        updated_at__lt=cutoff_date,
        status__in=[
            ConstructionTask.STATUS_PENDING,
            ConstructionTask.STATUS_IN_PROGRESS
        ]
    ).update(reminder_sent=False)
    
    logger.info(f'{updated} flags de lembrete resetadas')
    return {'reset_count': updated}
