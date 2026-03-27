import django_filters

from .models import Contract, Payment


class ContractFilter(django_filters.FilterSet):
    """
    Filters for Contract listings.
    created_at_after / created_at_before allow date-range queries.
    """
    created_at_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Criado a partir de (YYYY-MM-DD)',
    )
    created_at_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Criado até (YYYY-MM-DD)',
    )

    class Meta:
        model = Contract
        fields = [
            'status',
            'unit',
            'lead',
            'vendor',
            'created_at_after',
            'created_at_before',
        ]


class PaymentFilter(django_filters.FilterSet):
    """
    Filters for Payment listings.
    due_date_after / due_date_before allow date-range queries on the payment schedule.
    """
    due_date_after = django_filters.DateFilter(
        field_name='due_date',
        lookup_expr='gte',
        label='Vencimento a partir de (YYYY-MM-DD)',
    )
    due_date_before = django_filters.DateFilter(
        field_name='due_date',
        lookup_expr='lte',
        label='Vencimento até (YYYY-MM-DD)',
    )

    class Meta:
        model = Payment
        fields = [
            'contract',
            'status',
            'payment_type',
            'due_date_after',
            'due_date_before',
        ]
