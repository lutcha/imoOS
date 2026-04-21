"""
Construction API Views (ViewSets).

Endpoints:
- /phases/ - CRUD fases da obra
- /tasks/ - CRUD tasks (Simple + Advanced mode)
- /tasks/{id}/photos/ - Upload/listar fotos
- /tasks/{id}/progress/ - Timeline de progresso
- /dependencies/ - Gerenciar dependências (Advanced)
- /cpm/ - Dados CPM e recalcular
- /evm/ - Dashboard EVM e tendências
"""
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.users.permissions import IsTenantMember

from .models import (
    ConstructionPhase,
    ConstructionTask,
    TaskPhoto,
    TaskProgressLog,
    TaskDependency,
    CPMSnapshot,
    EVMSnapshot,
    DailyReport,
    ConstructionPhoto,
)
from .serializers import (
    ConstructionPhaseSerializer,
    ConstructionTaskSerializer,
    ConstructionTaskListSerializer,
    ConstructionTaskMobileSerializer,
    TaskPhotoSerializer,
    TaskProgressLogSerializer,
    TaskDependencySerializer,
    CPMSnapshotSerializer,
    EVMSnapshotSerializer,
    GanttDataSerializer,
    EVMTrendSerializer,
    TaskProgressUpdateSerializer,
    DailyReportSerializer,
    ConstructionPhotoSerializer,
)
from .services import CPMCalculator, EVMCalculator, ProgressUpdater
from .permissions import IsEngineerOrAdmin


# =============================================================================
# Daily Report (Diário de Obra) ViewSet
# =============================================================================

class DailyReportViewSet(viewsets.ModelViewSet):
    """ViewSet para o Diário de Obra."""
    
    queryset = DailyReport.objects.all().select_related('project', 'building', 'author').prefetch_related('photos')
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'building', 'status', 'date']
    search_fields = ['summary', 'weather']
    ordering_fields = ['date', 'created_at', 'progress_pct']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Mudar estado para SUBMITTED."""
        report = self.get_object()
        if report.status != DailyReport.STATUS_DRAFT:
            return Response(
                {'detail': 'Apenas rascunhos podem ser submetidos.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        report.status = DailyReport.STATUS_SUBMITTED
        report.save(update_fields=['status', 'updated_at'])
        return Response(DailyReportSerializer(report).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsEngineerOrAdmin])
    def approve(self, request, pk=None):
        """Aprovar relatório (requer permissão de engenheiro/admin)."""
        report = self.get_object()
        if report.status != DailyReport.STATUS_SUBMITTED:
            return Response(
                {'detail': 'Apenas relatórios submetidos podem ser aprovados.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        report.status = DailyReport.STATUS_APPROVED
        report.save(update_fields=['status', 'updated_at'])
        
        # Opcional: Aqui poderíamos disparar o recálculo do ConstructionProgress
        
        return Response(DailyReportSerializer(report).data)


class ConstructionPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet para fotos do Diário de Obra."""
    
    queryset = ConstructionPhoto.objects.all().select_related('report', 'created_by')
    serializer_class = ConstructionPhotoSerializer
    permission_classes = [IsAuthenticated, IsTenantMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# =============================================================================
# Phase ViewSet
# =============================================================================

class ConstructionPhaseViewSet(viewsets.ModelViewSet):
    """CRUD para fases da obra."""
    
    serializer_class = ConstructionPhaseSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['project', 'phase_type', 'status']
    ordering_fields = ['order', 'start_planned', 'created_at']
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def get_queryset(self):
        return ConstructionPhase.objects.filter(
            project__is_deleted=False
        ).select_related('project').order_by('order')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def recalculate_progress(self, request, pk=None):
        """Forçar recálculo do progresso da fase."""
        phase = self.get_object()
        phase.recalculate_progress()
        return Response(self.get_serializer(phase).data)


# =============================================================================
# Task ViewSet
# =============================================================================

class ConstructionTaskViewSet(viewsets.ModelViewSet):
    """CRUD para tasks de construção."""
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'phase', 'status', 'assigned_to', 'advanced_mode']
    search_fields = ['name', 'description', 'wbs_code']
    ordering_fields = ['due_date', 'priority', 'wbs_code', 'created_at']
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConstructionTaskListSerializer
        if self.action == 'mobile_list':
            return ConstructionTaskMobileSerializer
        return ConstructionTaskSerializer
    
    def get_queryset(self):
        queryset = ConstructionTask.objects.filter(
            project__is_deleted=False
        ).select_related(
            'phase', 'project', 'assigned_to', 'created_by'
        ).prefetch_related('photos')
        
        # Otimização para mobile
        if self.request.query_params.get('mobile') == 'true':
            return queryset.only(
                'id', 'wbs_code', 'name', 'status',
                'due_date', 'progress_percent',
                'assigned_to', 'phase'
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def mobile_list(self, request):
        """Endpoint otimizado para app mobile."""
        assigned_to = request.query_params.get('assigned_to')
        queryset = self.get_queryset()
        
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        serializer = ConstructionTaskMobileSerializer(
            queryset[:50],  # Limitar para mobile
            many=True
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Atualizar progresso da task."""
        task = self.get_object()
        serializer = TaskProgressUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updater = ProgressUpdater(task)
        log = updater.update(
            new_percent=serializer.validated_data['progress_percent'],
            updated_by=request.user,
            notes=serializer.validated_data.get('notes', ''),
            source='API'
        )
        
        if log:
            return Response({
                'task': ConstructionTaskSerializer(task).data,
                'log': TaskProgressLogSerializer(log).data
            })
        return Response(
            {'detail': 'Nenhuma alteração de progresso.'},
            status=status.HTTP_304_NOT_MODIFIED
        )
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Marcar task como iniciada."""
        task = self.get_object()
        task.start(user=request.user)
        return Response(ConstructionTaskSerializer(task).data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marcar task como concluída."""
        task = self.get_object()
        task.complete(user=request.user)
        return Response(ConstructionTaskSerializer(task).data)
    
    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        """Listar fotos da task."""
        task = self.get_object()
        photos = task.photos.all()
        serializer = TaskPhotoSerializer(photos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        """Upload de foto para a task."""
        task = self.get_object()
        serializer = TaskPhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        photo = serializer.save(task=task)
        
        # Atualizar progresso via foto se especificado
        if request.data.get('update_progress'):
            updater = ProgressUpdater(task)
            updater.update_from_photo(photo, user=request.user)
        
        return Response(
            TaskPhotoSerializer(photo).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def progress_timeline(self, request, pk=None):
        """Timeline de progresso da task."""
        task = self.get_object()
        logs = task.progress_logs.all()
        serializer = TaskProgressLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def enable_advanced_mode(self, request, pk=None):
        """Ativar modo avançado (CPM/EVM) para a task."""
        task = self.get_object()
        task.advanced_mode = ConstructionTask.ADVANCED_MODE_ON
        task.save(update_fields=['advanced_mode'])
        
        # Recalcular CPM do projeto
        calculator = CPMCalculator(str(task.project_id))
        stats = calculator.recalculate_project()
        
        return Response({
            'task': ConstructionTaskSerializer(task).data,
            'cpm_stats': stats
        })
    
    @action(detail=True, methods=['post'])
    def disable_advanced_mode(self, request, pk=None):
        """Desativar modo avançado."""
        task = self.get_object()
        task.advanced_mode = ConstructionTask.ADVANCED_MODE_OFF
        task.save(update_fields=['advanced_mode'])
        
        # Limpar dados CPM
        CPMSnapshot.objects.filter(task=task).delete()
        
        return Response(ConstructionTaskSerializer(task).data)


# =============================================================================
# Photo ViewSet
# =============================================================================

class TaskPhotoViewSet(viewsets.ModelViewSet):
    """CRUD para fotos de tasks."""
    
    serializer_class = TaskPhotoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task']
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def get_queryset(self):
        return TaskPhoto.objects.select_related('task', 'uploaded_by')
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


# =============================================================================
# Dependency ViewSet (Advanced Mode)
# =============================================================================

class TaskDependencyViewSet(viewsets.ModelViewSet):
    """Gerenciar dependências entre tasks (modo avançado)."""
    
    serializer_class = TaskDependencySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['from_task', 'to_task']
    permission_classes = [IsAuthenticated, IsEngineerOrAdmin]
    
    def get_queryset(self):
        return TaskDependency.objects.select_related('from_task', 'to_task')
    
    def perform_create(self, serializer):
        dependency = serializer.save()
        
        # Recalcular CPM após criar dependência
        if dependency.from_task.project_id:
            calculator = CPMCalculator(str(dependency.from_task.project_id))
            calculator.recalculate_project()
        
        return dependency
    
    def perform_destroy(self, instance):
        project_id = instance.from_task.project_id
        super().perform_destroy(instance)
        
        # Recalcular CPM após remover dependência
        if project_id:
            calculator = CPMCalculator(str(project_id))
            calculator.recalculate_project()


# =============================================================================
# CPM ViewSet (Advanced Mode)
# =============================================================================

class CPMViewSet(viewsets.ViewSet):
    """Endpoints para CPM (Critical Path Method)."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def list(self, request):
        """Listar dados CPM para um projeto."""
        project_id = request.query_params.get('project')
        if not project_id:
            return Response(
                {'detail': 'Parâmetro project é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        snapshots = CPMSnapshot.objects.filter(
            task__project_id=project_id
        ).select_related('task').order_by('task__wbs_code')
        
        serializer = CPMSnapshotSerializer(snapshots, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def recalculate(self, request):
        """Forçar recálculo do CPM para um projeto."""
        project_id = request.data.get('project')
        if not project_id:
            return Response(
                {'detail': 'Campo project é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        calculator = CPMCalculator(project_id)
        stats = calculator.recalculate_project()
        
        return Response({
            'status': 'success',
            'stats': stats
        })
    
    @action(detail=False, methods=['get'])
    def gantt(self, request):
        """Retornar dados para gráfico Gantt."""
        project_id = request.query_params.get('project')
        if not project_id:
            return Response(
                {'detail': 'Parâmetro project é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        calculator = CPMCalculator(project_id)
        gantt_data = calculator.get_gantt_data()
        
        return Response(gantt_data)
    
    @action(detail=False, methods=['get'])
    def critical_path(self, request):
        """Retornar apenas o caminho crítico."""
        project_id = request.query_params.get('project')
        if not project_id:
            return Response(
                {'detail': 'Parâmetro project é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        snapshots = CPMSnapshot.objects.filter(
            task__project_id=project_id,
            is_critical=True
        ).select_related('task').order_by('early_start')
        
        serializer = CPMSnapshotSerializer(snapshots, many=True)
        return Response(serializer.data)


# =============================================================================
# EVM ViewSet (Advanced Mode)
# =============================================================================

class EVMViewSet(viewsets.ViewSet):
    """Endpoints para EVM (Earned Value Management)."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def list(self, request):
        """Dashboard EVM para um projeto."""
        project_id = request.query_params.get('project')
        date_str = request.query_params.get('date')
        
        if not project_id:
            return Response(
                {'detail': 'Parâmetro project é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        calculator = EVMCalculator(project_id)
        
        from datetime import datetime
        as_of_date = None
        if date_str:
            try:
                as_of_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        data = calculator.calculate(as_of_date=as_of_date, save_snapshot=True)
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def trend(self, request):
        """Tendência EVM (S-curve) ao longo do tempo."""
        project_id = request.query_params.get('project')
        days = int(request.query_params.get('days', 30))
        
        if not project_id:
            return Response(
                {'detail': 'Parâmetro project é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        calculator = EVMCalculator(project_id)
        trend_data = calculator.get_trend_data(days=days)
        
        return Response(trend_data)
    
    @action(detail=False, methods=['get'])
    def forecast(self, request):
        """Previsões de prazo e custo."""
        project_id = request.query_params.get('project')
        
        if not project_id:
            return Response(
                {'detail': 'Parâmetro project é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        calculator = EVMCalculator(project_id)
        forecasts = calculator.get_forecast()
        
        return Response(forecasts)
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Forçar cálculo EVM e salvar snapshot."""
        project_id = request.data.get('project')
        date_str = request.data.get('date')
        
        if not project_id:
            return Response(
                {'detail': 'Campo project é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from datetime import datetime
        as_of_date = None
        if date_str:
            try:
                as_of_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'detail': 'Formato de data inválido. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        calculator = EVMCalculator(project_id)
        data = calculator.calculate(as_of_date=as_of_date, save_snapshot=True)
        
        return Response({
            'status': 'success',
            'data': data
        })


# =============================================================================
# Dashboard ViewSet
# =============================================================================

class ConstructionDashboardViewSet(viewsets.ViewSet):
    """Dashboard aggregado de construção."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    
    def list(self, request):
        """Resumo de construção para um projeto."""
        project_id = request.query_params.get('project')
        
        if not project_id:
            return Response(
                {'detail': 'Parâmetro project é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Estatísticas de tasks
        tasks = ConstructionTask.objects.filter(project_id=project_id)
        
        stats = {
            'tasks': {
                'total': tasks.count(),
                'pending': tasks.filter(status=ConstructionTask.STATUS_PENDING).count(),
                'in_progress': tasks.filter(status=ConstructionTask.STATUS_IN_PROGRESS).count(),
                'completed': tasks.filter(status=ConstructionTask.STATUS_COMPLETED).count(),
                'blocked': tasks.filter(status=ConstructionTask.STATUS_BLOCKED).count(),
                'overdue': tasks.filter(
                    status__in=[
                        ConstructionTask.STATUS_PENDING,
                        ConstructionTask.STATUS_IN_PROGRESS
                    ],
                    due_date__lt=timezone.now().date()
                ).count(),
            },
            'phases': {
                'total': ConstructionPhase.objects.filter(project_id=project_id).count(),
            },
            'progress': {
                'overall': 0,  # Calculado abaixo
            }
        }
        
        # Calcular progresso geral
        if stats['tasks']['total'] > 0:
            from django.db.models import Avg
            avg_progress = tasks.aggregate(avg=Avg('progress_percent'))['avg']
            stats['progress']['overall'] = round(avg_progress or 0, 2)
        
        # EVM summary (se houver)
        try:
            latest_evm = EVMSnapshot.objects.filter(
                project_id=project_id
            ).latest('date')
            stats['evm'] = {
                'spi': float(latest_evm.spi),
                'cpi': float(latest_evm.cpi),
                'health': latest_evm.overall_health
            }
        except EVMSnapshot.DoesNotExist:
            stats['evm'] = None
        
        return Response(stats)


# Import timezone no topo
from django.utils import timezone
