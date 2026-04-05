"""
Construction Admin.

Interface administrativa para:
- ConstructionPhase
- ConstructionTask
- TaskPhoto
- TaskDependency (Advanced)
- CPMSnapshot (Advanced)
- EVMSnapshot (Advanced)
"""
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    ConstructionPhase,
    ConstructionTask,
    TaskPhoto,
    TaskProgressLog,
    TaskDependency,
    CPMSnapshot,
    EVMSnapshot,
)


@admin.register(ConstructionPhase)
class ConstructionPhaseAdmin(SimpleHistoryAdmin):
    """Admin para fases da obra."""
    
    list_display = [
        'wbs_code', 'name', 'phase_type', 'project',
        'status', 'progress_percent',
        'start_planned', 'end_planned',
        'order'
    ]
    list_filter = ['project', 'phase_type', 'status']
    search_fields = ['name', 'description']
    ordering = ['project', 'order']
    date_hierarchy = 'start_planned'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('project', 'phase_type', 'name', 'description', 'order')
        }),
        ('Cronograma', {
            'fields': ('start_planned', 'end_planned', 'start_actual', 'end_actual')
        }),
        ('Status', {
            'fields': ('status', 'progress_percent')
        }),
    )
    
    actions = ['recalculate_progress', 'mark_completed']
    
    @admin.action(description='Recalcular progresso das fases selecionadas')
    def recalculate_progress(self, request, queryset):
        for phase in queryset:
            phase.recalculate_progress()
        self.message_user(request, f'{queryset.count()} fases recalculadas.')
    
    @admin.action(description='Marcar como concluídas')
    def mark_completed(self, request, queryset):
        queryset.update(status=ConstructionPhase.STATUS_COMPLETED)
        self.message_user(request, f'{queryset.count()} fases marcadas como concluídas.')
    
    def wbs_code(self, obj):
        """Retornar código WBS para ordenação."""
        return f'{obj.order}'
    wbs_code.short_description = 'WBS'


@admin.register(ConstructionTask)
class ConstructionTaskAdmin(SimpleHistoryAdmin):
    """Admin para tasks de construção."""
    
    list_display = [
        'wbs_code', 'name', 'phase', 'project',
        'status_badge', 'progress_bar',
        'assigned_to', 'due_date', 'is_overdue'
    ]
    list_filter = [
        'project', 'phase', 'status', 'priority',
        'advanced_mode', 'assigned_to'
    ]
    search_fields = ['name', 'description', 'wbs_code']
    ordering = ['phase', 'wbs_code']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('wbs_code', 'name', 'description', 'project', 'phase', 'building')
        }),
        ('Status', {
            'fields': ('status', 'priority', 'progress_percent')
        }),
        ('Atribuição', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Datas', {
            'fields': ('due_date', 'started_at', 'completed_at')
        }),
        ('Orçamento', {
            'fields': ('estimated_cost', 'actual_cost'),
            'classes': ('collapse',)
        }),
        ('Modo Avançado (CPM/EVM)', {
            'fields': ('advanced_mode', 'duration_days'),
            'classes': ('collapse',)
        }),
        ('BIM', {
            'fields': ('bim_element_ids',),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_completed', 'mark_in_progress', 'mark_pending',
        'enable_advanced_mode', 'disable_advanced_mode',
        'recalculate_cpm'
    ]
    
    @admin.action(description='Marcar como concluídas')
    def mark_completed(self, request, queryset):
        for task in queryset:
            task.complete(user=request.user)
        self.message_user(request, f'{queryset.count()} tasks concluídas.')
    
    @admin.action(description='Marcar como em andamento')
    def mark_in_progress(self, request, queryset):
        queryset.update(status=ConstructionTask.STATUS_IN_PROGRESS)
        self.message_user(request, f'{queryset.count()} tasks em andamento.')
    
    @admin.action(description='Marcar como pendentes')
    def mark_pending(self, request, queryset):
        queryset.update(status=ConstructionTask.STATUS_PENDING)
        self.message_user(request, f'{queryset.count()} tasks pendentes.')
    
    @admin.action(description='Ativar modo avançado (CPM/EVM)')
    def enable_advanced_mode(self, request, queryset):
        queryset.update(advanced_mode=ConstructionTask.ADVANCED_MODE_ON)
        self.message_user(request, f'{queryset.count()} tasks em modo avançado.')
    
    @admin.action(description='Desativar modo avançado')
    def disable_advanced_mode(self, request, queryset):
        queryset.update(advanced_mode=ConstructionTask.ADVANCED_MODE_OFF)
        self.message_user(request, f'{queryset.count()} tasks em modo simples.')
    
    @admin.action(description='Recalcular CPM para projetos selecionados')
    def recalculate_cpm(self, request, queryset):
        from .services import CPMCalculator
        projects = set(queryset.values_list('project_id', flat=True))
        for project_id in projects:
            calculator = CPMCalculator(str(project_id))
            calculator.recalculate_project()
        self.message_user(request, f'CPM recalculado para {len(projects)} projetos.')
    
    def status_badge(self, obj):
        """Retornar status com cor."""
        colors = {
            ConstructionTask.STATUS_PENDING: 'orange',
            ConstructionTask.STATUS_IN_PROGRESS: 'blue',
            ConstructionTask.STATUS_COMPLETED: 'green',
            ConstructionTask.STATUS_BLOCKED: 'red',
        }
        color = colors.get(obj.status, 'gray')
        return f'<span style="color: {color}; font-weight: bold;">{obj.get_status_display()}</span>'
    status_badge.short_description = 'Status'
    status_badge.allow_tags = True
    
    def progress_bar(self, obj):
        """Retornar barra de progresso."""
        return (
            f'<div style="width: 100px; background: #eee; border-radius: 3px;">'
            f'<div style="width: {obj.progress_percent}%; background: #4CAF50; '
            f'height: 20px; border-radius: 3px; text-align: center; color: white; '
            f'font-size: 12px; line-height: 20px;">{obj.progress_percent}%</div>'
            f'</div>'
        )
    progress_bar.short_description = 'Progresso'
    progress_bar.allow_tags = True
    
    def is_overdue(self, obj):
        """Indicador de atraso."""
        if obj.is_overdue:
            return f'⚠️ {obj.days_overdue} dias'
        return '✅ OK'
    is_overdue.short_description = 'Atraso'


@admin.register(TaskPhoto)
class TaskPhotoAdmin(admin.ModelAdmin):
    """Admin para fotos de tasks."""
    
    list_display = ['id', 'task', 'uploaded_by', 'has_geotag', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['task__name', 'caption']
    date_hierarchy = 'uploaded_at'


@admin.register(TaskProgressLog)
class TaskProgressLogAdmin(admin.ModelAdmin):
    """Admin para logs de progresso."""
    
    list_display = ['task', 'old_percent', 'new_percent', 'delta', 'updated_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['task__name']
    date_hierarchy = 'created_at'
    
    def delta(self, obj):
        """Diferença de progresso."""
        diff = obj.new_percent - obj.old_percent
        color = 'green' if diff > 0 else 'red' if diff < 0 else 'gray'
        return f'<span style="color: {color}">{diff:+.1f}%</span>'
    delta.short_description = 'Δ'
    delta.allow_tags = True


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    """Admin para dependências entre tasks (modo avançado)."""
    
    list_display = ['from_task', 'dependency_type', 'to_task', 'lag_days']
    list_filter = ['dependency_type']
    search_fields = ['from_task__name', 'to_task__name']


@admin.register(CPMSnapshot)
class CPMSnapshotAdmin(admin.ModelAdmin):
    """Admin para snapshots CPM (modo avançado)."""
    
    list_display = [
        'task', 'is_critical_badge',
        'early_start', 'early_finish',
        'total_float', 'calculated_at'
    ]
    list_filter = ['is_critical', 'calculated_at']
    search_fields = ['task__name', 'task__wbs_code']
    
    def is_critical_badge(self, obj):
        """Indicador de caminho crítico."""
        if obj.is_critical:
            return '🔴 CRÍTICO'
        return f'{obj.total_float}d'
    is_critical_badge.short_description = 'Caminho Crítico'


@admin.register(EVMSnapshot)
class EVMSnapshotAdmin(admin.ModelAdmin):
    """Admin para snapshots EVM (modo avançado)."""
    
    list_display = [
        'project', 'date',
        'spi_badge', 'cpi_badge',
        'ev', 'pv', 'ac',
        'overall_health'
    ]
    list_filter = ['date']
    search_fields = ['project__name']
    date_hierarchy = 'date'
    
    def spi_badge(self, obj):
        """SPI com cor."""
        color = 'green' if obj.spi >= 1 else 'orange' if obj.spi >= 0.9 else 'red'
        return f'<span style="color: {color}">{obj.spi}</span>'
    spi_badge.short_description = 'SPI'
    spi_badge.allow_tags = True
    
    def cpi_badge(self, obj):
        """CPI com cor."""
        color = 'green' if obj.cpi >= 1 else 'orange' if obj.cpi >= 0.9 else 'red'
        return f'<span style="color: {color}">{obj.cpi}</span>'
    cpi_badge.short_description = 'CPI'
    cpi_badge.allow_tags = True
