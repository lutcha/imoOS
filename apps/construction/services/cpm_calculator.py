"""
CPM Calculator - Algoritmo Critical Path Method.

Calcula Early/Late dates, identifica caminho crítico.
Usa topological sort para eficiência O(V + E).
"""
from collections import defaultdict, deque
from datetime import timedelta
from typing import List, Dict, Set, Tuple, Optional

from django.db import transaction
from django.utils import timezone

from ..models import ConstructionTask, TaskDependency, CPMSnapshot


class CPMCalculator:
    """
    Calculadora CPM (Critical Path Method).
    
    Algoritmo:
    1. Forward pass: calcular Early Start/Finish
    2. Backward pass: calcular Late Start/Finish
    3. Calcular float e identificar caminho crítico
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.tasks: Dict[str, ConstructionTask] = {}
        self.dependencies: Dict[str, List[str]] = defaultdict(list)  # task -> successors
        self.predecessors: Dict[str, List[str]] = defaultdict(list)  # task -> predecessors
        
    def load_data(self):
        """Carregar tasks e dependências do projeto."""
        # Apenas tasks em modo avançado
        tasks = ConstructionTask.objects.filter(
            project_id=self.project_id,
            advanced_mode=ConstructionTask.ADVANCED_MODE_ON
        ).select_related('cpm_data')
        
        self.tasks = {str(t.id): t for t in tasks}
        
        # Carregar dependências
        task_ids = set(self.tasks.keys())
        deps = TaskDependency.objects.filter(
            from_task_id__in=task_ids,
            to_task_id__in=task_ids
        )
        
        for dep in deps:
            from_id = str(dep.from_task_id)
            to_id = str(dep.to_task_id)
            self.dependencies[from_id].append(to_id)
            self.predecessors[to_id].append(from_id)
    
    def topological_sort(self) -> List[str]:
        """
        Ordenação topológica das tasks.
        Garante que processamos predecessors antes de successors.
        """
        in_degree = {task_id: len(self.predecessors[task_id]) for task_id in self.tasks}
        queue = deque([t for t in self.tasks if in_degree[t] == 0])
        result = []
        
        while queue:
            task_id = queue.popleft()
            result.append(task_id)
            
            for successor in self.dependencies[task_id]:
                in_degree[successor] -= 1
                if in_degree[successor] == 0:
                    queue.append(successor)
        
        # Verificar ciclo
        if len(result) != len(self.tasks):
            raise ValueError('Ciclo detectado nas dependências do projeto')
        
        return result
    
    def calculate_forward_pass(self) -> Dict[str, Tuple[timezone.datetime, timezone.datetime]]:
        """
        Forward pass: calcular Early Start e Early Finish.
        
        ES = max(EF of all predecessors)
        EF = ES + duration
        """
        sorted_tasks = self.topological_sort()
        early_dates: Dict[str, Tuple[timezone.datetime, timezone.datetime]] = {}
        
        for task_id in sorted_tasks:
            task = self.tasks[task_id]
            
            # Calcular ES baseado nos predecessors
            if not self.predecessors[task_id]:
                # Task inicial - usar start_planned da fase ou data atual
                if task.phase and task.phase.start_planned:
                    es = task.phase.start_planned
                else:
                    es = timezone.now().date()
            else:
                # ES = max(EF dos predecessors + lag)
                max_ef = None
                for pred_id in self.predecessors[task_id]:
                    pred_ef, _ = early_dates.get(pred_id, (es, es))
                    # Considerar lag
                    dep = self._get_dependency(pred_id, task_id)
                    lag = dep.lag_days if dep else 0
                    ef_with_lag = pred_ef + timedelta(days=lag)
                    if max_ef is None or ef_with_lag > max_ef:
                        max_ef = ef_with_lag
                es = max_ef
            
            # EF = ES + duration
            ef = es + timedelta(days=task.duration_days)
            early_dates[task_id] = (es, ef)
        
        return early_dates
    
    def calculate_backward_pass(
        self,
        early_dates: Dict[str, Tuple[timezone.datetime, timezone.datetime]]
    ) -> Dict[str, Tuple[timezone.datetime, timezone.datetime]]:
        """
        Backward pass: calcular Late Start e Late Finish.
        
        LF = min(LS of all successors)
        LS = LF - duration
        """
        sorted_tasks = self.topological_sort()
        late_dates: Dict[str, Tuple[timezone.datetime, timezone.datetime]] = {}
        
        # Encontrar LF do projeto (máximo EF)
        project_lf = max(ef for _, ef in early_dates.values())
        
        # Processar em ordem reversa
        for task_id in reversed(sorted_tasks):
            task = self.tasks[task_id]
            
            # Calcular LF baseado nos successors
            if not self.dependencies[task_id]:
                # Task final
                lf = project_lf
            else:
                # LF = min(LS dos successors - lag)
                min_ls = None
                for succ_id in self.dependencies[task_id]:
                    succ_ls, _ = late_dates.get(succ_id, (project_lf, project_lf))
                    # Considerar lag
                    dep = self._get_dependency(task_id, succ_id)
                    lag = dep.lag_days if dep else 0
                    ls_with_lag = succ_ls - timedelta(days=lag)
                    if min_ls is None or ls_with_lag < min_ls:
                        min_ls = ls_with_lag
                lf = min_ls
            
            # LS = LF - duration
            ls = lf - timedelta(days=task.duration_days)
            late_dates[task_id] = (ls, lf)
        
        return late_dates
    
    def identify_critical_path(
        self,
        early_dates: Dict[str, Tuple[timezone.datetime, timezone.datetime]],
        late_dates: Dict[str, Tuple[timezone.datetime, timezone.datetime]]
    ) -> Set[str]:
        """
        Identificar caminho crítico (tasks com float = 0).
        """
        critical_tasks = set()
        
        for task_id in self.tasks:
            es, ef = early_dates[task_id]
            ls, lf = late_dates[task_id]
            
            # Total float = LS - ES (ou LF - EF)
            total_float = (ls - es).days
            
            # No caminho crítico se float = 0
            if total_float == 0:
                critical_tasks.add(task_id)
        
        return critical_tasks
    
    def recalculate_project(self) -> Dict:
        """
        Recalcular todo o CPM e guardar snapshots.
        Retorna estatísticas do cálculo.
        """
        self.load_data()
        
        if not self.tasks:
            return {
                'tasks_processed': 0,
                'critical_path_length': 0,
                'project_duration_days': 0,
            }
        
        # Forward e backward pass
        early_dates = self.calculate_forward_pass()
        late_dates = self.calculate_backward_pass(early_dates)
        critical_tasks = self.identify_critical_path(early_dates, late_dates)
        
        # Salvar snapshots
        with transaction.atomic():
            for task_id in self.tasks:
                task = self.tasks[task_id]
                es, ef = early_dates[task_id]
                ls, lf = late_dates[task_id]
                
                # Calcular floats
                total_float = (ls - es).days
                
                # Free float = min(ES of successors) - EF
                free_float = total_float
                for succ_id in self.dependencies[task_id]:
                    succ_es, _ = early_dates[succ_id]
                    ff = (succ_es - ef).days
                    free_float = min(free_float, ff)
                
                # Criar ou atualizar snapshot
                CPMSnapshot.objects.update_or_create(
                    task=task,
                    defaults={
                        'early_start': es,
                        'early_finish': ef,
                        'late_start': ls,
                        'late_finish': lf,
                        'total_float': total_float,
                        'free_float': max(0, free_float),
                        'is_critical': task_id in critical_tasks,
                    }
                )
        
        # Calcular duração do projeto
        project_start = min(es for es, _ in early_dates.values())
        project_end = max(ef for _, ef in early_dates.values())
        duration_days = (project_end - project_start).days
        
        return {
            'tasks_processed': len(self.tasks),
            'critical_path_length': len(critical_tasks),
            'project_duration_days': duration_days,
            'project_start': project_start,
            'project_end': project_end,
        }
    
    def _get_dependency(self, from_task_id: str, to_task_id: str) -> Optional[TaskDependency]:
        """Buscar dependência entre duas tasks."""
        try:
            return TaskDependency.objects.get(
                from_task_id=from_task_id,
                to_task_id=to_task_id
            )
        except TaskDependency.DoesNotExist:
            return None
    
    def get_gantt_data(self) -> List[Dict]:
        """
        Retornar dados formatados para gráfico Gantt.
        """
        self.load_data()
        
        if not self.tasks:
            return []
        
        early_dates = self.calculate_forward_pass()
        late_dates = self.calculate_backward_pass(early_dates)
        critical_tasks = self.identify_critical_path(early_dates, late_dates)
        
        gantt_data = []
        for task_id, task in self.tasks.items():
            es, ef = early_dates[task_id]
            ls, lf = late_dates[task_id]
            
            gantt_data.append({
                'id': task_id,
                'wbs_code': task.wbs_code,
                'name': task.name,
                'start': es.isoformat(),
                'end': ef.isoformat(),
                'duration': task.duration_days,
                'progress': float(task.progress_percent),
                'is_critical': task_id in critical_tasks,
                'total_float': (ls - es).days,
                'dependencies': self.predecessors[task_id],
            })
        
        return sorted(gantt_data, key=lambda x: x['wbs_code'])
