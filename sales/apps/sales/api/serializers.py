from datetime import datetime
from decimal import Decimal

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from sales.apps.products.api.serializers import ProductSerializer

from ..models import SalesRecord


class SalesRecordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid')
    product = ProductSerializer(
        allow_null=True,  # in cases where product is deleted for whatever reason
    )
    total_sales_amount = serializers.DecimalField(
        max_digits=19,
        decimal_places=2,
        min_value=Decimal(0),
        default=Decimal(
            10000.00
        ),  # using default value for OpenAPI schema generation since it's read only serializer
        help_text=_('Total sales amount'),
    )

    class Meta:
        model = SalesRecord
        fields = [
            'id',
            'product',
            'quantity_sold',
            'total_sales_amount',
            'date_of_sale',
        ]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            _('Aggregated Sales Data by Month'),
            value={
                'group': '2024-08',
                'total_sales': '10000.00',
                'average_price': '500.00',
            },
        ),
        OpenApiExample(
            _('Aggregated Sales Data by Category'),
            value={
                'group': 'Electronics',
                'total_sales': '10000.00',
                'average_price': '500.00',
            },
        ),
    ]
)
class SalesDataAggregateSerializer(serializers.Serializer):
    group = serializers.SerializerMethodField(help_text=_('The grouping value'))
    total_sales = serializers.DecimalField(
        max_digits=19,
        decimal_places=2,
        min_value=Decimal(0),
        help_text=_('The total sales amount'),
    )
    average_price = serializers.DecimalField(
        max_digits=19,
        decimal_places=2,
        min_value=Decimal(0),
        help_text=_('Average price of sales'),
    )

    def get_group(self, obj: SalesRecord) -> str:
        group = obj['group']
        if isinstance(group, datetime):
            return group.strftime('%Y-%m')

        return group
