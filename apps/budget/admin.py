"""
Budget Admin — Admin customizado para o app budget.
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.budget.models import (
    LocalPriceItem, SimpleBudget, BudgetItem,
    CrowdsourcedPrice, UserPriceScore
)


@admin.register(LocalPriceItem)
class LocalPriceItemAdmin(admin.ModelAdmin):
    """Admin para itens da base de preços."""
    
    list_display = [
        'code', 'name', 'category_badge', 'unit', 
        'price_santiago', 'island_prices_summary', 
        'is_verified_badge', 'last_updated'
    ]
    list_filter = ['category', 'is_verified', 'last_updated']
    search_fields = ['name', 'code', 'description']
    list_editable = ['price_santiago']
    actions = ['mark_verified', 'mark_unverified', 'duplicate_item']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('code', 'name', 'description', 'category', 'unit')
        }),
        ('Preços por Ilha', {
            'fields': (
                ('price_santiago', 'price_sao_vicente'),
                ('price_sal', 'price_boa_vista'),
                ('price_santo_antao', 'price_sao_nicolau'),
                ('price_fogo', 'price_brava'),
                ('price_maio',),
            ),
            'description': 'Preços em CVE. Santiago é o preço base; outras ilhas usam Santiago como fallback se vazio.'
        }),
        ('Metadados', {
            'fields': ('source', 'is_verified', 'verified_by', 'ifc_class'),
            'classes': ('collapse',)
        }),
    )
    
    def category_badge(self, obj):
        """Mostrar categoria como badge colorido."""
        colors = {
            'MATERIALS': '#28a745',
            'LABOR': '#007bff',
            'EQUIPMENT': '#ffc107',
            'SERVICES': '#17a2b8',
        }
        color = colors.get(obj.category, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_category_display()
        )
    category_badge.short_description = 'Categoria'
    
    def is_verified_badge(self, obj):
        """Mostrar status de verificação como badge."""
        if obj.is_verified:
            return format_html(
                '<span style="color: #28a745;">✓ Verificado</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗ Pendente</span>'
        )
    is_verified_badge.short_description = 'Verificado'
    
    def island_prices_summary(self, obj):
        """Resumo de preços por ilha."""
        prices = obj.get_all_island_prices()
        defined = sum(1 for p in prices.values() if p is not None)
        return f'{defined}/9 ilhas'
    island_prices_summary.short_description = 'Preços Definidos'
    
    @admin.action(description='Marcar como verificado')
    def mark_verified(self, request, queryset):
        """Marcar items seleccionados como verificados."""
        updated = queryset.update(is_verified=True, verified_by=request.user)
        self.message_user(request, f'{updated} item(s) marcado(s) como verificado(s).')
    
    @admin.action(description='Marcar como não verificado')
    def mark_unverified(self, request, queryset):
        """Marcar items seleccionados como não verificados."""
        updated = queryset.update(is_verified=False, verified_by=None)
        self.message_user(request, f'{updated} item(s) marcado(s) como não verificado(s).')
    
    @admin.action(description='Duplicar item seleccionado')
    def duplicate_item(self, request, queryset):
        """Duplicar items seleccionados."""
        for item in queryset:
            item.pk = None
            item.code = f'{item.code}-COPY'
            item.is_verified = False
            item.save()
        self.message_user(request, f'{queryset.count()} item(s) duplicado(s).')


class BudgetItemInline(admin.TabularInline):
    """Inline para items de orçamento."""
    model = BudgetItem
    extra = 0
    fields = ['line_number', 'category', 'description', 'quantity', 'unit', 'unit_price', 'total']
    readonly_fields = ['total']
    ordering = ['line_number']


@admin.register(SimpleBudget)
class SimpleBudgetAdmin(admin.ModelAdmin):
    """Admin para orçamentos."""
    
    list_display = [
        'name', 'project', 'version', 'island', 
        'status_badge', 'item_count', 'grand_total_display', 
        'created_by', 'created_at'
    ]
    list_filter = ['status', 'island', 'created_at']
    search_fields = ['name', 'project__name', 'description']
    readonly_fields = [
        'total_materials', 'total_labor', 'total_equipment', 
        'total_services', 'subtotal', 'total_contingency', 
        'grand_total', 'created_at', 'updated_at'
    ]
    inlines = [BudgetItemInline]
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('project', 'name', 'version', 'description')
        }),
        ('Configuração', {
            'fields': ('island', 'currency', 'contingency_pct', 'status')
        }),
        ('Totais', {
            'fields': (
                ('total_materials', 'total_labor'),
                ('total_equipment', 'total_services'),
                'subtotal', 'total_contingency', 'grand_total'
            ),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_by', 'approved_by', 'created_at', 'updated_at', 'approved_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Mostrar status como badge."""
        colors = {
            'DRAFT': '#6c757d',
            'APPROVED': '#28a745',
            'BASELINE': '#007bff',
            'ARCHIVED': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def grand_total_display(self, obj):
        """Mostrar total formatado."""
        return f'{obj.grand_total:,.0f} CVE'
    grand_total_display.short_description = 'Total'
    
    def item_count(self, obj):
        """Número de items no orçamento."""
        return obj.items.count()
    item_count.short_description = 'Items'
    
    def category_totals(self, obj):
        """Para uso no list_filter (não implementado)."""
        return obj.grand_total


@admin.register(CrowdsourcedPrice)
class CrowdsourcedPriceAdmin(admin.ModelAdmin):
    """Admin para preços crowdsourced."""
    
    list_display = [
        'item_name', 'category', 'price_cve', 'island',
        'location', 'status_badge', 'reported_by', 
        'points_earned', 'created_at'
    ]
    list_filter = ['status', 'category', 'island', 'created_at']
    search_fields = ['item_name', 'location', 'supplier']
    actions = ['verify_prices', 'reject_prices']
    readonly_fields = ['points_earned', 'created_at']
    
    fieldsets = (
        ('Informação do Preço', {
            'fields': ('item_name', 'category', 'price_cve', 'unit')
        }),
        ('Localização', {
            'fields': ('island', 'location', 'supplier')
        }),
        ('Observação', {
            'fields': ('date_observed', 'receipt_photo')
        }),
        ('Status', {
            'fields': ('status', 'verified_by', 'verified_at', 'linked_price_item')
        }),
        ('Gamificação', {
            'fields': ('reported_by', 'points_earned'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Mostrar status como badge."""
        colors = {
            'PENDING': '#ffc107',
            'VERIFIED': '#28a745',
            'REJECTED': '#dc3545',
        }
        icons = {
            'PENDING': '⏳',
            'VERIFIED': '✓',
            'REJECTED': '✗',
        }
        color = colors.get(obj.status, '#6c757d')
        icon = icons.get(obj.status, '?')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    @admin.action(description='Verificar preços seleccionados (+10 pts)')
    def verify_prices(self, request, queryset):
        """Verificar preços seleccionados."""
        for price in queryset.filter(status='PENDING'):
            price.verify(request.user, points=10)
        self.message_user(
            request, 
            f'{queryset.filter(status="VERIFIED").count()} preço(s) verificado(s).'
        )
    
    @admin.action(description='Rejeitar preços seleccionados')
    def reject_prices(self, request, queryset):
        """Rejeitar preços seleccionados."""
        updated = queryset.filter(status='PENDING').update(
            status='REJECTED',
            verified_by=request.user
        )
        self.message_user(request, f'{updated} preço(s) rejeitado(s).')


@admin.register(UserPriceScore)
class UserPriceScoreAdmin(admin.ModelAdmin):
    """Admin para pontuações de utilizadores."""
    
    list_display = [
        'user', 'rank_badge', 'total_points', 
        'prices_reported', 'prices_verified'
    ]
    list_filter = ['rank']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['total_points', 'prices_reported', 'prices_verified']
    
    def rank_badge(self, obj):
        """Mostrar rank como badge."""
        colors = {
            'Novato': '#6c757d',
            'Contribuidor': '#17a2b8',
            'Especialista': '#007bff',
            'Guru': '#ffc107',
            'Lenda': '#28a745',
        }
        color = colors.get(obj.rank, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.rank
        )
    rank_badge.short_description = 'Rank'
