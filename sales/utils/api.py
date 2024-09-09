import importlib
import logging
import os

from django.apps import apps
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.routers import DefaultRouter
from drf_spectacular.utils import OpenApiResponse

logger = logging.getLogger(__name__)


class APIRouter(DefaultRouter):
    """
    Extended implementation of DRF `DefaultRouter` to autodiscover routes from each apps.

    Each app should contain an `api/` folder with `routes.py` file inside.

    Supports both DRF routes for viewsets and generic views(like `generics.ListAPIView`)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generic_routes = []
        self.auto_discover_routes()

    def auto_discover_routes(self):
        apps_dir = os.path.abspath(settings.APPS_DIR)

        for app_config in apps.get_app_configs():
            if os.path.commonpath([app_config.path, apps_dir]) == apps_dir:
                try:
                    routes_module = importlib.import_module(f'{app_config.name}.api.routes')
                    if hasattr(routes_module, 'router'):
                        for prefix, viewset, basename in routes_module.router.registry:
                            self.register(prefix, viewset, basename=basename)

                    if hasattr(routes_module, 'generic_routes'):
                        self.generic_routes += routes_module.generic_routes
                except ModuleNotFoundError:
                    if settings.DEBUG:
                        logger.warning(f'No api/routes.py file found for app: {app_config.name}')
                    continue

    def get_urls(self):
        urls = super().get_urls()
        return self.generic_routes + urls


class ErrorDetailResponseSerializer(serializers.Serializer):
    field_name = serializers.ListField(
        child=serializers.CharField(),
        help_text=_('List of error messages'),
    )


class BadRequestResponseSerializer(serializers.Serializer):
    detail = ErrorDetailResponseSerializer()


class UnauthorizedResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(help_text=_('Error message'))


class ForbiddenResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(help_text=_('Error message'))


class NotFoundResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(help_text=_('Error message'))


def get_schema_responses(serializer_class, detail=False):
    responses = {
        status.HTTP_200_OK: serializer_class() if detail else serializer_class(many=True),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
            description='Unauthorized - Authentication credentials were not provided.',
            response=UnauthorizedResponseSerializer,
        ),
        status.HTTP_403_FORBIDDEN: OpenApiResponse(
            description='Forbidden - You do not have permission to perform this action.',
            response=ForbiddenResponseSerializer,
        ),
    }

    if detail:
        responses = {
            **responses,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description='Not Found',
                response=NotFoundResponseSerializer,
            ),
        }
    else:
        responses = {
            **responses,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description='Bad Request',
                response=BadRequestResponseSerializer,
            ),
        }

    return responses
