import django_filters
from .models import Unit


class UnitFilter(django_filters.FilterSet):
    """
    Filters for Unit listings.
    price_cve_min / price_cve_max filter on the related UnitPricing.price_cve field.
    """
    price_cve_min = django_filters.NumberFilter(
        field_name='pricing__price_cve',
        lookup_expr='gte',
        label='Preço mínimo (CVE)',
    )
    price_cve_max = django_filters.NumberFilter(
        field_name='pricing__price_cve',
        lookup_expr='lte',
        label='Preço máximo (CVE)',
    )

    class Meta:
        model = Unit
        fields = [
            'status',
            'unit_type',
            'floor',
            'floor__building__project',
            'price_cve_min',
            'price_cve_max',
        ]
