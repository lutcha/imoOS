"""
Budget admin - ImoOS
Admin customizado para moderação de preços crowdsourced.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    PriceCategory, PriceItem, CrowdsourcedPrice,
    Budget, BudgetItem, UserPoints, PointsLog
)


@admin.register(PriceCategory)
class PriceCategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'code', 'item_count', 'is_active']
    list_display_links = ['name']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    ordering = ['code']
    
    def item_count(self, obj):
        return obj.items.filter(is_active=True).count()
    item_count.short_description = 'Itens Ativos'


@admin.register(PriceItem)
class PriceItemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'unit', 'price_santiago_display',
        'islands_with_prices', 'is_verified', 'source', 'last_updated'
    ]
    list_filter = ['category', 'is_active', 'is_verified', 'last_updated']
    search_fields = ['name', 'description']
    list_editable = ['is_verified']
    readonly_fields = ['last_updated', 'created_at', 'updated_at']
    fieldsets = (
        ('Informação Básica', {
            'fields': ('category', 'name', 'description', 'unit')
        }),
        ('Preços por Ilha', {
            'fields': (
                ('price_santiago', 'price_sao_vicente'),
                ('price_sal', 'price_boa_vista'),
                ('price_santo_antao', 'price_sao_nicolau'),
                ('price_maio', 'price_fogo'),
                ('price_brava',),
                'default_markup_pct',
            )
        }),
        ('Metadados', {
            'fields': ('is_active', 'is_verified', 'source', 'last_updated')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_santiago_display(self, obj):
        return f"{obj.price_santiago:,.0f} CVE"
    price_santiago_display.short_description = 'Preço Santiago'
    
    def islands_with_prices(self, obj):
        islands = obj.get_islands_with_prices()
        if not islands:
            return '-'
        return ', '.join([i.replace('_', ' ').title() for i in islands])
    islands_with_prices.short_description = 'Ilhas com Preços'


@admin.register(CrowdsourcedPrice)
class CrowdsourcedPriceAdmin(admin.ModelAdmin):
    list_display = [
        'item_name', 'price_cve', 'island', 'reporter',
        'status_badge', 'points_earned', 'date_reported'
    ]
    list_filter = ['status', 'island', 'reporter_role', 'date_reported']
    search_fields = ['item_name', 'supplier_name', 'reported_by__email']
    readonly_fields = [
        'points_earned', 'date_reported', 'reviewed_at',
        'linked_item', 'created_at', 'updated_at'
    ]
    actions = ['approve_prices', 'reject_prices']
    
    fieldsets = (
        ('Item', {
            'fields': ('item_name', 'category', 'price_cve', 'island', 'location_detail')
        }),
        ('Reporter', {
            'fields': ('reported_by', 'reporter_role', 'supplier_name')
        }),
        ('Moderação', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'review_notes', 'linked_item')
        }),
        ('Gamificação', {
            'fields': ('points_earned',)
        }),
        ('Timestamps', {
            'fields': ('date_reported', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def reporter(self, obj):
        return obj.reported_by.email
    reporter.short_description = 'Reportado por'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'APPROVED': 'green',
            'REJECTED': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approve_prices(self, request, queryset):
        """Ação para aprovar múltiplos preços"""
        from django.utils import timezone
        from decimal import Decimal
        
        approved_count = 0
        for price in queryset.filter(status='PENDING'):
            # Criar PriceItem
            category = price.category
            if not category:
                category, _ = PriceCategory.objects.get_or_create(
                    code='CROWD',
                    defaults={'name': 'Crowdsourced', 'icon': '👥'}
                )
            
            island_field = f"price_{price.island.lower()}"
            
            price_item, created = PriceItem.objects.get_or_create(
                name=price.item_name,
                category=category,
                defaults={
                    'unit': 'un',
                    'price_santiago': price.price_cve,
                    island_field: price.price_cve,
                    'source': f"Crowdsourced by {price.reported_by.email}",
                    'is_verified': True,
                }
            )
            
            if not created:
                setattr(price_item, island_field, price.price_cve)
                price_item.save()
            
            price.status = 'APPROVED'
            price.reviewed_by = request.user
            price.reviewed_at = timezone.now()
            price.linked_item = price_item
            price.save()
            
            # Bonus points
            user_points, _ = UserPoints.objects.get_or_create(user=price.reported_by)
            user_points.add_points(20, f"Preço aprovado: {price.item_name}")
            user_points.increment_prices_verified()
            
            approved_count += 1
        
        self.message_user(request, f'{approved_count} preços aprovados com sucesso.')
    approve_prices.short_description = 'Aprovar preços selecionados'
    
    def reject_prices(self, request, queryset):
        """Ação para rejeitar múltiplos preços"""
        from django.utils import timezone
        
        rejected_count = queryset.filter(status='PENDING').update(
            status='REJECTED',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{rejected_count} preços rejeitados.')
    reject_prices.short_description = 'Rejeitar preços selecionados'


class BudgetItemInline(admin.TabularInline):
    model = BudgetItem
    extra = 0
    fields = ['price_item', 'custom_name', 'quantity', 'unit_price', 'total', 'order']
    readonly_fields = ['total']
    autocomplete_fields = ['price_item']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'project', 'island', 'status',
        'subtotal', 'contingency', 'total', 'item_count', 'created_at'
    ]
    list_filter = ['status', 'island', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = [
        'total_materials', 'total_labor', 'total_equipment', 'total_services',
        'subtotal', 'contingency', 'total', 'created_at', 'updated_at'
    ]
    inlines = [BudgetItemInline]
    
    fieldsets = (
        ('Informação Básica', {
            'fields': ('name', 'description', 'project', 'island')
        }),
        ('Configuração', {
            'fields': ('contingency_pct', 'status')
        }),
        ('Totais', {
            'fields': (
                ('total_materials', 'total_labor'),
                ('total_equipment', 'total_services'),
                'subtotal',
                'contingency',
                'total',
            )
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Itens'


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'prices_reported', 'prices_verified', 'badges_list']
    list_filter = ['prices_reported', 'prices_verified']
    search_fields = ['user__email']
    readonly_fields = ['total_points', 'prices_reported', 'prices_verified']
    
    def badges_list(self, obj):
        if not obj.badges:
            return '-'
        badges_display = {
            'first_price': '🌟 Primeiro Preço',
            '10_prices': '🏆 10 Preços',
            '50_prices': '💎 50 Preços',
            'verified_reporter': '✅ Verificado',
        }
        return ', '.join([badges_display.get(b, b) for b in obj.badges])
    badges_list.short_description = 'Badges'


@admin.register(PointsLog)
class PointsLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'reason']
    readonly_fields = ['user', 'points', 'reason', 'created_at']
