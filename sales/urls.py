"""
URL configuration for sales project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .utils.api import APIRouter

router = APIRouter()


class RestrictedSchemaView(SpectacularAPIView):
    permission_classes = [IsAuthenticated]


class RestrictedSwaggerView(SpectacularSwaggerView):
    permission_classes = [IsAuthenticated]


class ScopedTokenObtainPairView(TokenObtainPairView):
    throttle_scope = 'token_obtain'


class ScopedTokenRefreshView(TokenRefreshView):
    throttle_scope = 'token_refresh'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', ScopedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', ScopedTokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', RestrictedSchemaView.as_view(), name='schema'),
    path('api/docs/', RestrictedSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]


if settings.ENABLE_DEBUG_TOOLBAR:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
