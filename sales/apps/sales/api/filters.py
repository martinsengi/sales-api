from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError

from sales.utils.helpers import convert_date_to_utc

from ..models import SalesRecord

if TYPE_CHECKING:
    from django.db.models import QuerySet  # pragma: no cover


class SalesRecordFilter(filters.FilterSet):
    start_date = filters.DateFilter(
        method='filter_start_date',
        label=_('Start date (ISO 8601)'),
        help_text=_('Filters records from this date (format: YYYY-MM-DD)'),
    )
    end_date = filters.DateFilter(
        method='filter_end_date',
        label=_('End date (ISO 8601)'),
        help_text=_('Filter records up to this date (format: YYYY-MM-DD)'),
    )
    category = filters.CharFilter(
        field_name='product__category',
        lookup_expr='icontains',
        label=_('Category'),
        help_text=_('Filter records by partial match on their product category'),
    )

    class Meta:
        model = SalesRecord
        fields = [
            'start_date',
            'end_date',
            'category',
        ]

    def filter_start_date(self, queryset: 'QuerySet[SalesRecord]', name, value):
        if value:
            start_datetime = convert_date_to_utc(date=value)
            queryset = queryset.filter(date_of_sale__gte=start_datetime)
        return queryset

    def filter_end_date(self, queryset: 'QuerySet[SalesRecord]', name, value):
        if value:
            end_datetime = convert_date_to_utc(date=value, is_end_of_day=True)
            queryset = queryset.filter(date_of_sale__lte=end_datetime)
        return queryset

    def filter_queryset(self, queryset: 'QuerySet[SalesRecord]'):
        start_date = self.form.cleaned_data.get('start_date')
        end_date = self.form.cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise ValidationError(
                detail={
                    'start_date': ['Must be before or equal to end_date.'],
                }
            )

        return super().filter_queryset(queryset)


class SalesRecordAggregateFilter(SalesRecordFilter):
    aggregate_by = filters.ChoiceFilter(
        choices=SalesRecord.AGGREGATE_BY_CHOICES.choices,
        required=True,
        method='filter_aggregate_by',
        label=_('Aggregation parameter'),
    )

    class Meta:
        model = SalesRecord
        fields = [
            'start_date',
            'end_date',
            'category',
            'aggregate_by',
        ]

    def filter_aggregate_by(self, queryset: 'QuerySet[SalesRecord]', name: str, value: str):
        return SalesRecord.get_data_aggregated_queryset(queryset=queryset, aggregate_by=value)
