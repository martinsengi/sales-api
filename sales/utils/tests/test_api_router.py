from unittest import TestCase
from unittest.mock import MagicMock, patch

from django.conf import settings

from sales.utils.api import APIRouter


class APIRouterTest(TestCase):
    def setUp(self):
        self.router = APIRouter()

    @patch('sales.utils.api_router.importlib.import_module')
    @patch('sales.utils.api_router.apps.get_app_configs')
    def test_auto_discover_routes_with_valid_routes(
        self,
        mock_get_app_configs,
        mock_import_module,
    ):
        mock_app_config = MagicMock()
        mock_app_config.path = settings.APPS_DIR / 'test_app'
        mock_app_config.name = 'test_app'
        mock_get_app_configs.return_value = [mock_app_config]

        mock_routes_module = MagicMock()
        mock_import_module.return_value = mock_routes_module
        mock_routes_module.router.registry = [('prefix', 'viewset', 'basename')]

        self.router.auto_discover_routes()
        self.assertIn(('prefix', 'viewset', 'basename'), self.router.registry)

    @patch('sales.utils.api_router.importlib.import_module')
    @patch('sales.utils.api_router.apps.get_app_configs')
    @patch('sales.utils.api_router.settings.DEBUG', True)
    def test_auto_discover_routes_with_missing_routes_file(
        self,
        mock_get_app_configs,
        mock_import_module,
    ):
        mock_app_config_1 = MagicMock()
        mock_app_config_1.path = '/app_with_routes'
        mock_app_config_1.name = 'app_with_routes'

        mock_app_config_2 = MagicMock()
        mock_app_config_2.path = '/app_without_routes'
        mock_app_config_2.name = 'app_without_routes'

        mock_get_app_configs.return_value = [mock_app_config_1, mock_app_config_2]

        def side_effect(app_name):
            if app_name == 'app_without_routes.api.routes':
                raise ModuleNotFoundError
            return MagicMock()

        mock_import_module.side_effect = side_effect

        with self.assertLogs('sales.utils.api_router', level='WARNING') as log:
            router = APIRouter()
            router.auto_discover_routes()

        # Ensure the warning is logged for the second app
        self.assertIn('No api/routes.py file found for app: app_without_routes', log.output[0])

        # Ensure that the first app with routes is processed correctly
        mock_import_module.assert_any_call('app_with_routes.api.routes')

    @patch('sales.utils.api_router.importlib.import_module')
    @patch('sales.utils.api_router.apps.get_app_configs')
    def test_auto_discover_generic_routes(self, mock_get_app_configs, mock_import_module):
        mock_app_config = MagicMock()
        mock_app_config.path = settings.APPS_DIR / 'test_app_with_generic_routes'
        mock_app_config.name = 'test_app_with_generic_routes'
        mock_get_app_configs.return_value = [mock_app_config]

        mock_routes_module = MagicMock()
        mock_import_module.return_value = mock_routes_module
        mock_routes_module.generic_routes = ['generic_route']

        self.router.auto_discover_routes()
        self.assertIn('generic_route', self.router.generic_routes)
