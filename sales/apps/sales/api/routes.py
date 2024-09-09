from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import SalesDataAggregateView, SalesRecordViewSet

router = DefaultRouter()

router.register(r'sales-data', SalesRecordViewSet, basename='sales-data')

generic_routes = [
    path('sales-data/aggregate/', SalesDataAggregateView.as_view(), name='sales-data-aggregate'),
]
