from django_filters import rest_framework as filters

from .models import DailyReport


class DailyReportFilter(filters.FilterSet):
    project = filters.UUIDFilter(field_name='project__id')
    building = filters.UUIDFilter(field_name='building__id')
    status = filters.ChoiceFilter(choices=DailyReport.STATUS_CHOICES)
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')
    author = filters.UUIDFilter(field_name='author__id')

    class Meta:
        model = DailyReport
        fields = ['project', 'building', 'status', 'date_from', 'date_to', 'author']
