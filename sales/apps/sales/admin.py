from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import SalesRecord


@admin.register(SalesRecord)
class SalesRecordAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'product',
        'quantity_sold',
        'get_total_sales_amount',
        'date_of_sale',
    )
    search_fields = (
        'uuid',
        'product__uuid',
        'product__category',
    )

    def get_total_sales_amount(self, obj: SalesRecord) -> str:
        return f'{obj.total_sales_amount:.2f}'

    get_total_sales_amount.short_description = _('total sales amount')

    def get_queryset(self, request: HttpRequest) -> QuerySet[SalesRecord]:
        return super().get_queryset(request).select_related('product')
