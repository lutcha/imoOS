"""
Budget filters - ImoOS
Filtros para preços, orçamentos e gamificação.
"""
import django_filters
from .models import PriceItem, Budget, CrowdsourcedPrice


class PriceItemFilter(django_filters.FilterSet):
    """Filtros para PriceItem"""
    category_code = django_filters.CharFilter(field_name='category__code')
    min_price = django_filters.NumberFilter(field_name='price_santiago', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_santiago', lookup_expr='lte')
    is_verified = django_filters.BooleanFilter()
    has_island_price = django_filters.CharFilter(method='filter_has_island_price')
    
    class Meta:
        model = PriceItem
        fields = ['category', 'category_code', 'is_active', 'is_verified']
    
    def filter_has_island_price(self, queryset, name, value):
        """Filtra itens que têm preço definido para uma ilha específica"""
        island_field = f'price_{value.lower()}'
        if hasattr(PriceItem, island_field):
            return queryset.exclude(**{island_field: None})
        return queryset


class BudgetFilter(django_filters.FilterSet):
    """Filtros para Budget"""
    project_id = django_filters.UUIDFilter(field_name='project__id')
    status = django_filters.MultipleChoiceFilter(choices=Budget.STATUS_CHOICES)
    island = django_filters.MultipleChoiceFilter(choices=PriceItem.ISLANDS)
    min_total = django_filters.NumberFilter(field_name='total', lookup_expr='gte')
    max_total = django_filters.NumberFilter(field_name='total', lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Budget
        fields = ['project', 'island', 'status']


class CrowdsourcedPriceFilter(django_filters.FilterSet):
    """Filtros para CrowdsourcedPrice"""
    status = django_filters.MultipleChoiceFilter(choices=CrowdsourcedPrice.STATUS_CHOICES)
    island = django_filters.MultipleChoiceFilter(choices=PriceItem.ISLANDS)
    my_reports = django_filters.BooleanFilter(method='filter_my_reports')
    
    class Meta:
        model = CrowdsourcedPrice
        fields = ['status', 'island', 'category']
    
    def filter_my_reports(self, queryset, name, value):
        """Filtra apenas preços reportados pelo utilizador atual"""
        if value and self.request:
            return queryset.filter(reported_by=self.request.user)
        return queryset
