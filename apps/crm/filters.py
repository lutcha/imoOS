import django_filters
from .models import Lead


class LeadFilter(django_filters.FilterSet):
    """
    Filters for Lead listings.
    budget_min / budget_max filter the Lead.budget field (CVE).
    """
    budget_min = django_filters.NumberFilter(
        field_name='budget',
        lookup_expr='gte',
        label='Orçamento mínimo (CVE)',
    )
    budget_max = django_filters.NumberFilter(
        field_name='budget',
        lookup_expr='lte',
        label='Orçamento máximo (CVE)',
    )

    class Meta:
        model = Lead
        fields = [
            'status',
            'source',
            'assigned_to',
            'preferred_typology',
            'budget_min',
            'budget_max',
        ]
