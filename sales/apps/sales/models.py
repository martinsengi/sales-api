import uuid
from typing import TYPE_CHECKING, Optional

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from sales.apps.products.models import Product

from .interfaces import ProductSnapshot

if TYPE_CHECKING:
    from django.db.models import Expression, QuerySet  # pragma: no cover


class SalesRecord(models.Model):
    class AggregateByChoices(models.TextChoices):
        MONTH = 'month', _('Month')
        CATEGORY = 'category', _('Category')

    AGGREGATE_BY_CHOICES = AggregateByChoices

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('product'),
    )
    product_snapshot: ProductSnapshot = models.JSONField(default=dict)
    quantity_sold = models.PositiveIntegerField(
        _('quantity sold'),
        default=1,
        validators=[MinValueValidator(1)],
    )
    total_sales_amount = models.DecimalField(
        _('total sales amount'),
        default=0,
        max_digits=19,
        decimal_places=4,
        validators=[MinValueValidator(0)],
    )
    date_of_sale = models.DateTimeField(_('date of sale'), default=timezone.now)

    class Meta:
        verbose_name = _('sales record')
        verbose_name_plural = _('sales records')
        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['date_of_sale']),
        ]

    def __str__(self) -> str:
        return f'{self.product.name} {self.id}'

    def save(self, *args, **kwargs) -> None:
        if not self.pk and self.product:
            self.product_snapshot = ProductSnapshot(
                name=self.product.name,
                category=self.product.category,
                price=str(self.product.price),
            )
        super().save(*args, **kwargs)

    @staticmethod
    def _get_data_aggregated_queryset(
        queryset: 'QuerySet[SalesRecord]',
        aggregation_expression: 'Expression',
    ):
        """
        Perform aggregation on the sales records queryset
        based on the provided aggregation expression.

        Args:
            queryset (`QuerySet[SalesRecord]`):
                The queryset of `SalesRecord` instances to be aggregated.
            aggregation_expression (`Expression`):
                The aggregation expression defining how to group the results.

        Returns:
            QuerySet: A queryset with annotations for `group`, `total_sales`, and `average_price`.
        """

        return (
            queryset.filter(quantity_sold__gt=0)
            .annotate(group=aggregation_expression)
            .values('group')
            .annotate(
                total_sales=models.Sum('total_sales_amount'),
                average_price=models.Avg(
                    models.F('total_sales_amount') / models.F('quantity_sold'),
                    output_field=models.DecimalField(),
                ),
            )
            .order_by('group')
        )

    @classmethod
    def get_data_aggregated_queryset(
        cls,
        aggregate_by: 'SalesRecord.AggregateByChoices',
        queryset: 'Optional[QuerySet[SalesRecord]]' = None,
    ):
        """
        Returns a queryset of aggregated sales data based on the aggregation type provided.

        Args:
            aggregate_by (`SalesRecord.AggregateByChoices`):
                The parameter specifying the aggregation type.
            queryset (`Optional[QuerySet[SalesRecord]]`):
                A custom queryset to aggregate.
                If `None`, falls back to default queryset of all existing `SalesRecord`.

        Returns:
            QuerySet:
                A queryset with aggregated data including total sales and average price per group.
        """

        if queryset is None:
            queryset = cls.objects.all().select_related('product')

        aggregation_expression = None

        if aggregate_by == cls.AGGREGATE_BY_CHOICES.MONTH:
            aggregation_expression = TruncMonth('date_of_sale')

        elif aggregate_by == cls.AGGREGATE_BY_CHOICES.CATEGORY:
            aggregation_expression = models.Case(
                models.When(product__isnull=True, then=models.Value('Unknown')),
                default=models.F('product__category'),
                output_field=models.CharField(),
            )

        assert aggregation_expression is not None, 'Invalid SaleRecord aggregation attempt'

        return cls._get_data_aggregated_queryset(
            queryset=queryset,
            aggregation_expression=aggregation_expression,
        )
