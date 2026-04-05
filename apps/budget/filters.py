"""
Budget filters — Filtros para preços, orçamentos e gamificação.
"""
import django_filters
from apps.budget.models import LocalPriceItem, SimpleBudget, CrowdsourcedPrice


class LocalPriceItemFilter(django_filters.FilterSet):
    """Filtros para LocalPriceItem"""
    min_price = django_filters.NumberFilter(field_name='price_santiago', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_santiago', lookup_expr='lte')
    is_verified = django_filters.BooleanFilter()
    has_island_price = django_filters.CharFilter(method='filter_has_island_price')
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = LocalPriceItem
        fields = ['category', 'is_verified', 'unit']
    
    def filter_has_island_price(self, queryset, name, value):
        """Filtra itens que têm preço definido para uma ilha específica"""
        island_map = {
            'santiago': 'price_santiago',
            'sao_vicente': 'price_sao_vicente',
            'sal': 'price_sal',
            'boa_vista': 'price_boa_vista',
            'santo_antao': 'price_santo_antao',
            'sao_nicolau': 'price_sao_nicolau',
            'fogo': 'price_fogo',
            'brava': 'price_brava',
            'maio': 'price_maio',
        }
        field = island_map.get(value.lower())
        if field:
            return queryset.exclude(**{field: None})
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Busca em nome, código e descrição"""
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(code__icontains=value) |
            models.Q(description__icontains=value)
        )


class SimpleBudgetFilter(django_filters.FilterSet):
    """Filtros para SimpleBudget"""
    project_id = django_filters.UUIDFilter(field_name='project__id')
    status = django_filters.MultipleChoiceFilter(choices=SimpleBudget.STATUS_CHOICES)
    island = django_filters.MultipleChoiceFilter(choices=LocalPriceItem.ISLAND_CHOICES)
    min_total = django_filters.NumberFilter(field_name='grand_total', lookup_expr='gte')
    max_total = django_filters.NumberFilter(field_name='grand_total', lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = SimpleBudget
        fields = ['project', 'island', 'status', 'currency']


class CrowdsourcedPriceFilter(django_filters.FilterSet):
    """Filtros para CrowdsourcedPrice"""
    status = django_filters.MultipleChoiceFilter(choices=CrowdsourcedPrice.STATUS_CHOICES)
    island = django_filters.MultipleChoiceFilter(choices=LocalPriceItem.ISLAND_CHOICES)
    my_reports = django_filters.BooleanFilter(method='filter_my_reports')
    min_price = django_filters.NumberFilter(field_name='price_cve', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_cve', lookup_expr='lte')
    
    class Meta:
        model = CrowdsourcedPrice
        fields = ['status', 'island', 'category']
    
    def filter_my_reports(self, queryset, name, value):
        """Filtra apenas preços reportados pelo utilizador atual"""
        if value and self.request:
            return queryset.filter(reported_by=self.request.user)
        return queryset


# Import no final para evitar circular import
from django.db import models
