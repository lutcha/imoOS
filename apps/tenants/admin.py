"""
Django Admin configuration for Super-Admin management of tenants.
Accessible only to users with is_staff=True.
"""
from django.contrib import admin
from django.utils.html import format_html
from django_tenants.utils import schema_context
from .models import Client, Domain, TenantSettings, PlanEvent


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin interface for managing tenants (promotoras).
    Allows super-admin to view, suspend, and activate tenants.
    """
    list_display = ['name', 'schema_name', 'plan', 'is_active', 'country', 'created_at', 'tenant_health']
    list_filter = ['plan', 'is_active', 'country']
    search_fields = ['name', 'schema_name', 'slug']
    readonly_fields = ['schema_name', 'slug', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informação Básica', {
            'fields': ('name', 'slug', 'schema_name')
        }),
        ('Plano & Configuração', {
            'fields': ('plan', 'is_active', 'country', 'currency', 'timezone')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['suspend_tenants', 'activate_tenants', 'export_tenants_csv']

    def tenant_health(self, obj):
        """Check if tenant has settings configured."""
        settings = TenantSettings.objects.filter(tenant=obj).first()
        if not settings:
            return format_html('<span style="color:red">⚠ Sem settings</span>')
        
        # Check if any projects exist in tenant schema
        try:
            with schema_context(obj.schema_name):
                from apps.projects.models import Project
                project_count = Project.objects.count()
            return format_html(
                '<span style="color:green">✓ OK</span> ({} projectos)',
                project_count
            )
        except Exception:
            return format_html('<span style="color:orange">⚠ Erro DB</span>')
    tenant_health.short_description = 'Health'

    @admin.action(description='Suspender tenants seleccionados')
    def suspend_tenants(self, request, queryset):
        """Suspend selected tenants (soft delete)."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} tenant(s) suspenso(s).')
        
        # Log the action
        for tenant in queryset:
            PlanEvent.objects.create(
                tenant=tenant,
                event_type=PlanEvent.EVENT_LIMIT_HIT,
                from_plan=tenant.plan,
                to_plan=tenant.plan,
                metadata={'action': 'suspended', 'by': request.user.email},
                created_by=request.user,
            )

    @admin.action(description='Activar tenants seleccionados')
    def activate_tenants(self, request, queryset):
        """Activate selected tenants."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} tenant(s) activado(s).')

    @admin.action(description='Exportar lista de tenants (CSV)')
    def export_tenants_csv(self, request, queryset):
        """Export tenant list as CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tenants_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Nome', 'Schema', 'Slug', 'Plano', 'Activo', 
            'País', 'Projectos', 'Data Criação'
        ])
        
        for tenant in queryset:
            project_count = 0
            try:
                with schema_context(tenant.schema_name):
                    from apps.projects.models import Project
                    project_count = Project.objects.count()
            except Exception:
                project_count = -1
            
            writer.writerow([
                tenant.id,
                tenant.name,
                tenant.schema_name,
                tenant.slug,
                tenant.plan,
                'Sim' if tenant.is_active else 'Não',
                tenant.country,
                project_count,
                tenant.created_at.strftime('%Y-%m-%d %H:%M'),
            ])
        
        return response


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """Admin interface for managing tenant domains."""
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['domain', 'tenant__name']
    readonly_fields = ['domain', 'tenant', 'is_primary']

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of primary domains."""
        if obj and obj.is_primary:
            return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        """Domains are created automatically with tenants."""
        return False


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    """Admin interface for tenant-specific settings."""
    list_display = ['tenant', 'plan', 'max_projects', 'max_units', 'max_users', 'imocv_enabled']
    list_filter = ['imocv_enabled']
    search_fields = ['tenant__name', 'tenant__schema_name']
    
    def plan(self, obj):
        return obj.tenant.plan if obj.tenant else 'N/A'
    plan.short_description = 'Plano'

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion — settings should be preserved."""
        return False


@admin.register(PlanEvent)
class PlanEventAdmin(admin.ModelAdmin):
    """
    Immutable audit log of tenant plan events.
    Read-only — no edits or deletions allowed.
    """
    list_display = ['tenant', 'event_type', 'from_plan', 'to_plan', 'created_by', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['tenant__name', 'created_by__email']
    readonly_fields = [
        'id', 'tenant', 'event_type', 'from_plan', 'to_plan', 
        'metadata', 'created_by', 'created_at'
    ]
    
    fieldsets = (
        ('Evento', {
            'fields': ('id', 'event_type', 'created_at')
        }),
        ('Tenant', {
            'fields': ('tenant',)
        }),
        ('Detalhes do Plano', {
            'fields': ('from_plan', 'to_plan'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Autor', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )
    
    # Imutável — sem edição
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
