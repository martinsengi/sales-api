from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ReadOnlyModelViewSet
from sales.utils.api import get_schema_responses
from sales.utils.mixins import AuthenticatedViewMixin

from ..models import SalesRecord
from .filters import SalesRecordAggregateFilter, SalesRecordFilter
from .serializers import SalesDataAggregateSerializer, SalesRecordSerializer


class PageBasedPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema_view(
    list=extend_schema(
        summary='Sales Records list',
        description=(
            'Fetch a paginated list of `SalesRecord` entities, including sales quantity, '
            'total sales amount, and product details.',
        ),
        responses=get_schema_responses(serializer_class=SalesRecordSerializer),
    ),
    retrieve=extend_schema(
        summary='Sales Records retrieve',
        description=(
            'Fetch details of a single `SalesRecord` entity by its UUID, including sales quantity, '
            'total sales amount, and associated product details.',
        ),
        responses=get_schema_responses(serializer_class=SalesRecordSerializer, detail=True),
    ),
)
class SalesRecordViewSet(AuthenticatedViewMixin, ReadOnlyModelViewSet):
    lookup_field = 'uuid'
    queryset = SalesRecord.objects.select_related('product').order_by('-date_of_sale')
    serializer_class = SalesRecordSerializer
    pagination_class = PageBasedPagination
    filterset_class = SalesRecordFilter

    @method_decorator(cache_page(60 * 20, key_prefix='api_salesrecord_list'), name='list')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    get=extend_schema(
        summary='Aggregate Sales Data',
        description=(
            'Endpoint for data aggregation of `SalesRecord` instances by grouping parameter.'
        ),
        responses=get_schema_responses(serializer_class=SalesDataAggregateSerializer),
    )
)
class SalesDataAggregateView(AuthenticatedViewMixin, ListAPIView):
    queryset = SalesRecord.objects.select_related('product').order_by('-date_of_sale')
    serializer_class = SalesDataAggregateSerializer
    filterset_class = SalesRecordAggregateFilter

    @method_decorator(cache_page(60 * 20, key_prefix='api_salesdataaggregate_list'), name='list')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
