"""
Progress Updater - Atualização de progresso das tasks.

Suporta:
- Atualização manual (slider 0-100)
- Atualização via BIM (futuro)
- Atualização via fotos (ML futuro)
- Logs automáticos de alterações
"""
from decimal import Decimal
from typing import Optional

from django.utils import timezone

from ..models import ConstructionTask, TaskPhoto, TaskProgressLog


class ProgressUpdater:
    """
    Gerenciador de atualizações de progresso.
    
    Responsabilidades:
    - Validar alterações de progresso
    - Criar logs de alteração
    - Atualizar status da task
    - Notificar fase pai
    """
    
    def __init__(self, task: ConstructionTask):
        self.task = task
    
    def update(
        self,
        new_percent: Decimal,
        updated_by,
        notes: str = '',
        source: str = 'MANUAL'
    ) -> TaskProgressLog:
        """
        Atualizar progresso da task.
        
        Args:
            new_percent: Novo valor (0-100)
            updated_by: User que fez a atualização
            notes: Notas opcionais
            source: Fonte da atualização (MANUAL, BIM, PHOTO, MOBILE)
            
        Returns:
            TaskProgressLog criado
        """
        # Validar range
        new_percent = max(Decimal('0'), min(Decimal('100'), new_percent))
        
        old_percent = self.task.progress_percent
        
        # Não criar log se não houve mudança significativa (> 0.01%)
        if abs(new_percent - old_percent) < Decimal('0.01'):
            return None
        
        # Criar log
        log = TaskProgressLog.objects.create(
            task=self.task,
            updated_by=updated_by,
            old_percent=old_percent,
            new_percent=new_percent,
            notes=f'[{source}] {notes}'.strip()
        )
        
        # Atualizar task
        self.task.progress_percent = new_percent
        
        # Auto-update status
        if new_percent >= 100:
            self.task.status = ConstructionTask.STATUS_COMPLETED
            if not self.task.completed_at:
                self.task.completed_at = timezone.now()
        elif new_percent > 0:
            if self.task.status == ConstructionTask.STATUS_PENDING:
                self.task.status = ConstructionTask.STATUS_IN_PROGRESS
                if not self.task.started_at:
                    self.task.started_at = timezone.now()
        
        self.task.save(update_fields=[
            'progress_percent', 'status', 'started_at', 'completed_at'
        ])
        
        # Recalcular progresso da fase
        if self.task.phase:
            self.task.phase.recalculate_progress()
        
        return log
    
    def update_from_photo(
        self,
        photo: TaskPhoto,
        estimated_percent: Optional[Decimal] = None,
        user=None
    ) -> Optional[TaskProgressLog]:
        """
        Atualizar progresso baseado em foto (placeholder para ML futuro).
        
        Por agora, apenas registra a foto com o progresso atual.
        No futuro, pode usar ML para estimar progresso.
        """
        # Guardar progresso no momento da foto
        photo.progress_at_upload = self.task.progress_percent
        photo.save(update_fields=['progress_at_upload'])
        
        # Se foi fornecida estimativa, aplicar
        if estimated_percent is not None and user:
            return self.update(
                new_percent=estimated_percent,
                updated_by=user,
                notes=f'Foto #{photo.id} carregada',
                source='PHOTO'
            )
        
        return None
    
    def update_from_bim(
        self,
        bim_progress: Decimal,
        updated_by,
        element_ids: list = None
    ) -> TaskProgressLog:
        """
        Atualizar progresso via integração BIM (futuro).
        
        Args:
            bim_progress: Progresso reportado pelo modelo BIM
            updated_by: User/engineer
            element_ids: Lista de elementos BIM atualizados
        """
        notes = ''
        if element_ids:
            notes = f'Elementos BIM: {", ".join(element_ids[:5])}'
            if len(element_ids) > 5:
                notes += f' e mais {len(element_ids) - 5}'
            
            # Atualizar lista de elementos na task
            current_elements = set(self.task.bim_element_ids or [])
            current_elements.update(element_ids)
            self.task.bim_element_ids = list(current_elements)
            self.task.save(update_fields=['bim_element_ids'])
        
        return self.update(
            new_percent=bim_progress,
            updated_by=updated_by,
            notes=notes,
            source='BIM'
        )
    
    def bulk_update_tasks(
        self,
        updates: list,
        updated_by
    ) -> list:
        """
        Atualizar múltiplas tasks de uma vez.
        
        Args:
            updates: Lista de dicts com {'task_id': str, 'percent': Decimal, 'notes': str}
            updated_by: User
            
        Returns:
            Lista de TaskProgressLog criados
        """
        logs = []
        
        for update in updates:
            try:
                task = ConstructionTask.objects.get(id=update['task_id'])
                updater = ProgressUpdater(task)
                log = updater.update(
                    new_percent=update['percent'],
                    updated_by=updated_by,
                    notes=update.get('notes', ''),
                    source=update.get('source', 'BULK')
                )
                if log:
                    logs.append(log)
            except ConstructionTask.DoesNotExist:
                continue
        
        return logs
    
    def get_progress_velocity(self, days: int = 7) -> Decimal:
        """
        Calcular velocidade de progresso (pontos percentuais por dia).
        
        Útil para prever quando a task será completada.
        """
        from datetime import timedelta
        
        since = timezone.now() - timedelta(days=days)
        logs = TaskProgressLog.objects.filter(
            task=self.task,
            created_at__gte=since
        ).order_by('created_at')
        
        if logs.count() < 2:
            return Decimal('0')
        
        first = logs.first()
        last = logs.last()
        
        delta_progress = last.new_percent - first.old_percent
        delta_days = (last.created_at - first.created_at).days or 1
        
        velocity = delta_progress / Decimal(delta_days)
        return velocity
    
    def estimate_completion(self) -> Optional[timezone.datetime]:
        """
        Estimar data de conclusão baseada na velocidade atual.
        
        Returns:
            Data estimada ou None se já completada
        """
        if self.task.status == ConstructionTask.STATUS_COMPLETED:
            return self.task.completed_at
        
        remaining = Decimal('100') - self.task.progress_percent
        if remaining <= 0:
            return timezone.now()
        
        velocity = self.get_progress_velocity(days=14)  # Usar 14 dias para média
        
        if velocity <= 0:
            return None  # Sem progresso recente, não é possível estimar
        
        days_remaining = remaining / velocity
        return timezone.now() + timezone.timedelta(days=float(days_remaining))
