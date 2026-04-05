"""
EVM Calculator - Earned Value Management.

Calcula:
- PV (Planned Value): Valor planejado até a data
- EV (Earned Value): Valor ganho (trabalho realizado)
- AC (Actual Cost): Custo real
- SPI, CPI: Índices de performance
- EAC, ETC, VAC: Previsões
"""
from datetime import date
from decimal import Decimal
from typing import Dict, Optional

from django.db import transaction
from django.utils import timezone

from ..models import ConstructionTask, EVMSnapshot


class EVMCalculator:
    """
    Calculadora EVM (Earned Value Management).
    
    Fórmulas:
    - PV = Σ(budget of tasks planned to be done by date)
    - EV = Σ(budget × % complete of each task)
    - AC = Σ(actual cost reported)
    - SPI = EV / PV (>1 = adiantado)
    - CPI = EV / AC (>1 = abaixo orçamento)
    - EAC = BAC / CPI
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        
    def calculate(
        self,
        as_of_date: Optional[date] = None,
        save_snapshot: bool = True
    ) -> Dict:
        """
        Calcular EVM para o projeto.
        
        Args:
            as_of_date: Data de corte (default: hoje)
            save_snapshot: Se True, salva EVMSnapshot
            
        Returns:
            Dicionário com todas as métricas EVM
        """
        if as_of_date is None:
            as_of_date = timezone.now().date()
        
        # Buscar todas as tasks do projeto
        tasks = ConstructionTask.objects.filter(project_id=self.project_id)
        
        # Contadores
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status=ConstructionTask.STATUS_COMPLETED).count()
        in_progress_tasks = tasks.filter(status=ConstructionTask.STATUS_IN_PROGRESS).count()
        
        # Valores base (BAC - Budget at Completion)
        bac = sum(t.estimated_cost for t in tasks)
        
        # Calcular PV, EV, AC
        pv = Decimal('0.00')
        ev = Decimal('0.00')
        ac = Decimal('0.00')
        
        for task in tasks:
            task_budget = task.estimated_cost or Decimal('0.00')
            task_actual = task.actual_cost or Decimal('0.00')
            task_progress = Decimal(str(task.progress_percent)) / 100
            
            # EV = budget × % complete
            ev += task_budget * task_progress
            
            # AC = actual cost reported
            ac += task_actual
            
            # PV = budget se a task deveria estar completa
            # Simplificação: se due_date <= as_of_date, deveria estar feita
            if task.due_date <= as_of_date:
                pv += task_budget
            else:
                # Task ainda não deveria estar completa
                # Calcular proporcional ao tempo decorrido
                if task.phase and task.phase.start_planned:
                    phase_start = task.phase.start_planned
                    phase_end = task.phase.end_planned
                    if phase_end > phase_start:
                        total_duration = (phase_end - phase_start).days
                        elapsed = (as_of_date - phase_start).days
                        if elapsed > 0:
                            planned_progress = min(Decimal(elapsed) / Decimal(total_duration), Decimal('1.0'))
                            pv += task_budget * planned_progress
        
        # Calcular índices
        spi = Decimal('1.00')
        if pv > 0:
            spi = (ev / pv).quantize(Decimal('0.01'))
        
        cpi = Decimal('1.00')
        if ac > 0:
            cpi = (ev / ac).quantize(Decimal('0.01'))
        
        # Variâncias
        sv = ev - pv
        cv = ev - ac
        
        # Previsões
        eac = bac
        if cpi > 0:
            eac = (bac / cpi).quantize(Decimal('0.01'))
        
        etc = eac - ac
        vac = bac - eac
        
        # TCPI
        tcpi = None
        denominator = bac - ac
        if denominator > 0:
            tcpi = ((bac - ev) / denominator).quantize(Decimal('0.01'))
        
        result = {
            'date': as_of_date,
            'bac': bac,
            'pv': pv,
            'ev': ev,
            'ac': ac,
            'spi': spi,
            'cpi': cpi,
            'sv': sv,
            'cv': cv,
            'eac': eac,
            'etc': etc,
            'vac': vac,
            'tcpi': tcpi,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
        }
        
        # Salvar snapshot
        if save_snapshot:
            self._save_snapshot(result)
        
        return result
    
    def _save_snapshot(self, data: Dict):
        """Salvar resultado como EVMSnapshot."""
        with transaction.atomic():
            snapshot, created = EVMSnapshot.objects.update_or_create(
                project_id=self.project_id,
                date=data['date'],
                defaults={
                    'bac': data['bac'],
                    'pv': data['pv'],
                    'ev': data['ev'],
                    'ac': data['ac'],
                    'spi': data['spi'],
                    'cpi': data['cpi'],
                    'sv': data['sv'],
                    'cv': data['cv'],
                    'eac': data['eac'],
                    'etc': data['etc'],
                    'vac': data['vac'],
                    'tcpi': data['tcpi'],
                    'total_tasks': data['total_tasks'],
                    'completed_tasks': data['completed_tasks'],
                    'in_progress_tasks': data['in_progress_tasks'],
                }
            )
        return snapshot
    
    def get_trend_data(self, days: int = 30) -> Dict:
        """
        Retornar dados para curva S (S-curve) - tendência ao longo do tempo.
        
        Returns:
            Dados para gráfico de evolução de PV, EV, AC
        """
        from datetime import timedelta
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        snapshots = EVMSnapshot.objects.filter(
            project_id=self.project_id,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        if not snapshots.exists():
            # Calcular snapshot atual se não houver histórico
            self.calculate(save_snapshot=True)
            snapshots = EVMSnapshot.objects.filter(
                project_id=self.project_id,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
        
        trend = {
            'dates': [],
            'pv': [],
            'ev': [],
            'ac': [],
            'spi': [],
            'cpi': [],
        }
        
        for snap in snapshots:
            trend['dates'].append(snap.date.isoformat())
            trend['pv'].append(float(snap.pv))
            trend['ev'].append(float(snap.ev))
            trend['ac'].append(float(snap.ac))
            trend['spi'].append(float(snap.spi))
            trend['cpi'].append(float(snap.cpi))
        
        return trend
    
    def get_forecast(self, data: Optional[Dict] = None) -> Dict:
        """
        Calcular previsões de prazo e custo.
        
        Returns:
            Previsões baseadas no desempenho atual
        """
        if data is None:
            data = self.calculate(save_snapshot=False)
        
        spi = data['spi']
        cpi = data['cpi']
        bac = data['bac']
        eac = data['eac']
        
        # Buscar dados do projeto
        from apps.projects.models import Project
        try:
            project = Project.objects.get(id=self.project_id)
            planned_duration = None
            if project.start_date and project.expected_completion:
                planned_duration = (project.expected_completion - project.start_date).days
        except Project.DoesNotExist:
            planned_duration = None
        
        forecasts = {
            'cost_forecast': {
                'eac': eac,
                'vac': data['vac'],
                'status': 'ON_BUDGET' if cpi >= 0.95 else 'OVER_BUDGET',
                'trend': 'IMPROVING' if cpi > 1 else 'DECLINING',
            },
            'schedule_forecast': {
                'spi': spi,
                'status': 'ON_SCHEDULE' if spi >= 0.95 else 'BEHIND',
                'trend': 'IMPROVING' if spi > 1 else 'DECLINING',
            },
            'recommendations': [],
        }
        
        # Recomendações
        if cpi < 0.9:
            forecasts['recommendations'].append(
                'Custo acima do orçamento. Revisar recursos e eficiência.'
            )
        if spi < 0.9:
            forecasts['recommendations'].append(
                'Cronograma atrasado. Considerar compressão de prazo ou escopo.'
            )
        if cpi > 1.1 and spi > 1.1:
            forecasts['recommendations'].append(
                'Projeto performando acima do esperado. Verificar qualidade.'
            )
        
        # Previsão de término
        if planned_duration and spi > 0:
            projected_duration = int(planned_duration / float(spi))
            if project.start_date:
                projected_end = project.start_date + timezone.timedelta(days=projected_duration)
                forecasts['schedule_forecast']['projected_end_date'] = projected_end.isoformat()
        
        return forecasts
