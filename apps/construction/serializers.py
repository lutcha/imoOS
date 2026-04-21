"""
Construction API Serializers.

Inclui serializers para:
- ConstructionPhase (fases da obra)
- ConstructionTask (tasks simples + avançadas)
- TaskPhoto (fotos com geolocalização)
- CPM/EVM (modo avançado)
"""
from rest_framework import serializers

from apps.users.serializers import UserSerializer
from apps.projects.serializers import ProjectSerializer, BuildingSerializer

from .models import (
    DailyReport,
    ConstructionPhoto,
    ConstructionPhase,
    ConstructionTask,
    TaskPhoto,
    TaskProgressLog,
    TaskDependency,
    CPMSnapshot,
    EVMSnapshot,
    ConstructionProject,
)


# =============================================================================
# Phase Serializers
# =============================================================================

class ConstructionPhaseSerializer(serializers.ModelSerializer):
    """Serializer completo para fases."""
    
    progress_percent = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    deadline_deviation_days = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ConstructionPhase
        fields = [
            'id', 'project', 'phase_type', 'name', 'description',
            'start_planned', 'end_planned', 'start_actual', 'end_actual',
            'status', 'progress_percent', 'order',
            'deadline_deviation_days', 'task_count', 'completed_task_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def get_completed_task_count(self, obj):
        return obj.tasks.filter(status=ConstructionTask.STATUS_COMPLETED).count()


class ConstructionPhaseListSerializer(serializers.ModelSerializer):
    """Serializer leve para listagens."""
    
    class Meta:
        model = ConstructionPhase
        fields = ['id', 'phase_type', 'name', 'status', 'progress_percent', 'order']


# =============================================================================
# Task Serializers
# =============================================================================

class ConstructionTaskSerializer(serializers.ModelSerializer):
    """Serializer completo para tasks."""
    
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    created_by = UserSerializer(read_only=True)
    phase = ConstructionPhaseListSerializer(read_only=True)
    phase_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    # CPM data (apenas modo avançado)
    cpm_data = serializers.SerializerMethodField()
    is_critical = serializers.BooleanField(read_only=True)
    total_float = serializers.IntegerField(read_only=True, allow_null=True)
    
    # Propriedades calculadas
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ConstructionTask
        fields = [
            'id', 'wbs_code', 'name', 'description',
            'phase', 'phase_id',
            'project', 'building',
            'assigned_to', 'assigned_to_id', 'created_by',
            'status', 'priority',
            'due_date', 'started_at', 'completed_at',
            'progress_percent',
            'estimated_cost', 'actual_cost',
            'advanced_mode', 'duration_days',
            'bim_element_ids',
            'is_overdue', 'days_overdue', 'days_until_due',
            'cpm_data', 'is_critical', 'total_float',
            'reminder_sent', 'overdue_notified',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def get_cpm_data(self, obj):
        """Retornar dados CPM se modo avançado estiver ligado."""
        if obj.advanced_mode == ConstructionTask.ADVANCED_MODE_OFF:
            return None
        
        try:
            cpm = obj.cpm_data
            return {
                'early_start': cpm.early_start,
                'early_finish': cpm.early_finish,
                'late_start': cpm.late_start,
                'late_finish': cpm.late_finish,
                'total_float': cpm.total_float,
                'free_float': cpm.free_float,
                'is_critical': cpm.is_critical,
            }
        except CPMSnapshot.DoesNotExist:
            return None
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ConstructionTaskListSerializer(serializers.ModelSerializer):
    """Serializer leve para listagens (API mobile)."""
    
    assigned_to_name = serializers.CharField(
        source='assigned_to.get_full_name',
        read_only=True,
        default=''
    )
    phase_name = serializers.CharField(source='phase.name', read_only=True)
    
    class Meta:
        model = ConstructionTask
        fields = [
            'id', 'wbs_code', 'name', 'status', 'priority',
            'due_date', 'progress_percent',
            'assigned_to_name', 'phase_name',
            'is_overdue',
        ]


class ConstructionTaskMobileSerializer(serializers.ModelSerializer):
    """Serializer otimizado para app mobile (menos campos, fast)."""
    
    class Meta:
        model = ConstructionTask
        fields = [
            'id', 'wbs_code', 'name', 'status',
            'due_date', 'progress_percent',
            'assigned_to', 'phase',
        ]


class TaskProgressUpdateSerializer(serializers.Serializer):
    """Serializer para atualização de progresso."""
    progress_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)


# =============================================================================
# Photo Serializers
# =============================================================================

class TaskPhotoSerializer(serializers.ModelSerializer):
    """Serializer para fotos de tasks."""
    
    uploaded_by = UserSerializer(read_only=True)
    has_geotag = serializers.BooleanField(read_only=True)
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskPhoto
        fields = [
            'id', 'task', 'uploaded_by',
            'image', 'image_url', 'thumbnail', 'thumbnail_url',
            'caption', 'latitude', 'longitude',
            'taken_at', 'progress_at_upload',
            'uploaded_at',
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return obj.thumbnail.url
        return None
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskProgressLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de progresso."""
    
    updated_by = UserSerializer(read_only=True)
    delta = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = TaskProgressLog
        fields = ['id', 'old_percent', 'new_percent', 'delta', 'notes', 'updated_by', 'created_at']


# =============================================================================
# CPM Serializers
# =============================================================================

class TaskDependencySerializer(serializers.ModelSerializer):
    """Serializer para dependências entre tasks."""
    
    from_task_wbs = serializers.CharField(source='from_task.wbs_code', read_only=True)
    to_task_wbs = serializers.CharField(source='to_task.wbs_code', read_only=True)
    
    class Meta:
        model = TaskDependency
        fields = [
            'id', 'from_task', 'from_task_wbs',
            'to_task', 'to_task_wbs',
            'dependency_type', 'lag_days',
            'created_at',
        ]


class CPMSnapshotSerializer(serializers.ModelSerializer):
    """Serializer para snapshots CPM."""
    
    task_wbs = serializers.CharField(source='task.wbs_code', read_only=True)
    task_name = serializers.CharField(source='task.name', read_only=True)
    
    class Meta:
        model = CPMSnapshot
        fields = [
            'task_wbs', 'task_name',
            'early_start', 'early_finish',
            'late_start', 'late_finish',
            'total_float', 'free_float', 'is_critical',
            'calculated_at',
        ]


class GanttDataSerializer(serializers.Serializer):
    """Serializer para dados do gráfico Gantt."""
    id = serializers.UUIDField()
    wbs_code = serializers.CharField()
    name = serializers.CharField()
    start = serializers.DateField()
    end = serializers.DateField()
    duration = serializers.IntegerField()
    progress = serializers.FloatField()
    is_critical = serializers.BooleanField()
    total_float = serializers.IntegerField()
    dependencies = serializers.ListField(child=serializers.CharField())


# =============================================================================
# EVM Serializers
# =============================================================================

class EVMSnapshotSerializer(serializers.ModelSerializer):
    """Serializer para snapshots EVM."""
    
    schedule_status = serializers.CharField(read_only=True)
    cost_status = serializers.CharField(read_only=True)
    overall_health = serializers.CharField(read_only=True)
    
    class Meta:
        model = EVMSnapshot
        fields = [
            'date', 'bac', 'pv', 'ev', 'ac',
            'spi', 'cpi', 'sv', 'cv',
            'eac', 'etc', 'vac', 'tcpi',
            'schedule_status', 'cost_status', 'overall_health',
            'total_tasks', 'completed_tasks', 'in_progress_tasks',
            'created_at',
        ]


class EVMTrendSerializer(serializers.Serializer):
    """Serializer para tendência EVM (S-curve)."""
    dates = serializers.ListField(child=serializers.DateField())
    pv = serializers.ListField(child=serializers.FloatField())
    ev = serializers.ListField(child=serializers.FloatField())
    ac = serializers.ListField(child=serializers.FloatField())
    spi = serializers.ListField(child=serializers.FloatField())
    cpi = serializers.ListField(child=serializers.FloatField())


class ConstructionPhotoSerializer(serializers.ModelSerializer):
    """Serializer para fotos do diário de obra."""
    
    class Meta:
        model = ConstructionPhoto
        fields = [
            'id', 'report', 's3_key', 'thumbnail_s3_key', 'caption',
            'latitude', 'longitude', 'has_geotag', 'created_by', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class DailyReportSerializer(serializers.ModelSerializer):
    """Serializer para o diário de obra (versão simples)."""
    
    author = UserSerializer(read_only=True)
    photos = ConstructionPhotoSerializer(many=True, read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    building_name = serializers.CharField(source='building.name', read_only=True, allow_null=True)
    
    class Meta:
        model = DailyReport
        fields = [
            'id', 'project', 'project_name', 'building', 'building_name',
            'date', 'author', 'summary', 'progress_pct', 'status',
            'weather', 'workers_count', 'photos', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


# =============================================================================
# ConstructionProject Serializer
# =============================================================================

class ConstructionProjectSerializer(serializers.ModelSerializer):
    """Serializer para projetos de obra (ConstructionProject)."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status = serializers.SerializerMethodField()
    overall_progress_pct = serializers.FloatField(source='progress_percent', read_only=True)
    is_delayed = serializers.BooleanField(read_only=True)
    sales_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    budget_cve = serializers.DecimalField(source='estimated_construction_cost', max_digits=12, decimal_places=2, read_only=True)
    actual_cost_cve = serializers.DecimalField(source='actual_construction_cost', max_digits=12, decimal_places=2, read_only=True)
    start_date = serializers.DateField(source='start_planned', read_only=True)
    expected_end_date = serializers.DateField(source='end_planned', read_only=True)
    actual_end_date = serializers.DateField(source='end_actual', read_only=True)

    class Meta:
        model = ConstructionProject
        fields = [
            'id', 'name', 'description', 'status', 'status_display',
            'contract', 'project', 'building', 'unit',
            'start_date', 'expected_end_date', 'actual_end_date',
            'bim_model_s3_key', 'overall_progress_pct', 'is_delayed',
            'sales_value', 'budget_cve', 'actual_cost_cve',
            'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'created_by', 'created_at', 'updated_at', 
            'overall_progress_pct', 'is_delayed',
            'sales_value', 'budget_cve', 'actual_cost_cve',
            'start_date', 'expected_end_date', 'actual_end_date',
        ]

    def get_status(self, obj):
        """Map status to frontend expectations (IN_PROGRESS -> ACTIVE)."""
        if obj.status == 'IN_PROGRESS':
            return 'ACTIVE'
        return obj.status
