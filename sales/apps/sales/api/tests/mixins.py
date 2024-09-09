from datetime import datetime, timezone
from unittest.mock import call, patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone as django_timezone
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

from sales.apps.products.models import Product

from ...models import SalesRecord


class SalesRecordAPITestMixin:
    """
    Mixin that contains reusable test cases that involve common filtering,
    date validation and cache invalidation for Sales Record API endpoints.
    """

    def setUp(self):
        self.product = Product.objects.create(
            name='Test Product',
            category='Test Category',
            price=100.00,
        )

        SalesRecord.objects.create(
            product=self.product,
            quantity_sold=5,
            total_sales_amount=self.product.price * 5,
            date_of_sale=django_timezone.make_aware(datetime(2024, 9, 1, 0, 0, 0), timezone.utc),
        )

    @property
    def url_name(self):
        raise NotImplementedError(
            '`url_name` property must be set when using `SalesRecordTestMixin`',
        )

    @property
    def aggregate_by(self):
        return getattr(self, 'default_aggregate_by', None)

    @property
    def _default_params(self):
        params = {}
        if self.aggregate_by:
            params['aggregate_by'] = self.aggregate_by

        return params

    def _get_response_data(self, response):
        if self.aggregate_by:
            return response.data
        return response.data['results']

    def test_list_fetch(self):
        response = self.client.get(reverse(self.url_name), self._default_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(self._get_response_data(response=response)) > 0)

    def test_list_filtered_by_non_existent_category(self):
        response = self.client.get(
            reverse(self.url_name),
            {
                **self._default_params,
                'category': 'Idontexist',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self._get_response_data(response=response)), 0)

    def test_list_invalid_start_date(self):
        response = self.client.get(
            reverse(self.url_name),
            {
                **self._default_params,
                'start_date': '22222',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_invalid_end_date(self):
        response = self.client.get(
            reverse(self.url_name),
            {
                **self._default_params,
                'end_date': '22222',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_no_records(self):
        SalesRecord.objects.all().delete()
        response = self.client.get(
            reverse(self.url_name),
            self._default_params,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self._get_response_data(response=response)), 0)

    def test_list_invalid_date_range(self):
        start_date = django_timezone.now().strftime('%Y-%m-%d')
        end_date = (django_timezone.now() - django_timezone.timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(
            reverse(self.url_name),
            {
                **self._default_params,
                'start_date': start_date,
                'end_date': end_date,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_random_query_parameters(self):
        response = self.client.get(
            reverse(self.url_name),
            {
                **self._default_params,
                'random_param': 'random_value',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(self._get_response_data(response=response)) > 0)

    def test_filter_by_exact_date_has_result(self):
        with django_timezone.override('Europe/Sofia'):  # UTC + 3
            response = self.client.get(
                reverse(self.url_name),
                {
                    **self._default_params,
                    'start_date': '2024-09-01',  # 2024-08-31 21:00:00 UTC
                    'end_date': '2024-09-01',  # 2024-09-01 20:59:59 UTC
                },
            )

            # SalesRecord in setUp is 2024-09-01 00:00:00 UTC
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(self._get_response_data(response=response)), 1)

    def test_filter_by_exact_date_no_result(self):
        with django_timezone.override('America/Los_Angeles'):  # UTC - 7
            response = self.client.get(
                reverse(self.url_name),
                {
                    **self._default_params,
                    'start_date': '2024-09-01',  # 2024-09-01 07:00:00 UTC
                    'end_date': '2024-09-01',  # 2024-09-02 06:59:59 UTC
                },
            )

            # SalesRecord in setUp is 2024-09-01 00:00:00 UTC
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(self._get_response_data(response)), 0)

    @patch('django.core.cache.cache.delete_pattern')
    def test_cache_invalidation_on_create(self, mock_delete_pattern):
        cache.clear()

        self.client.get(
            reverse(self.url_name),
            self._default_params,
        )
        SalesRecord.objects.create(
            product=self.product,
            quantity_sold=10,
            total_sales_amount=1000.00,
            date_of_sale=django_timezone.now(),
        )

        mock_delete_pattern.assert_has_calls(
            [
                call('*api_salesrecord_list*'),
                call('*api_salesdataaggregate_list*'),
            ],
            any_order=True,
        )

    @patch('django.core.cache.cache.delete_pattern')
    def test_cache_invalidation_on_update(self, mock_delete_pattern):
        cache.clear()

        self.client.get(
            reverse(self.url_name),
            self._default_params,
        )
        sales_record = SalesRecord.objects.last()
        sales_record.quantity_sold = 10
        sales_record.save()

        mock_delete_pattern.assert_has_calls(
            [
                call('*api_salesrecord_list*'),
                call('*api_salesdataaggregate_list*'),
            ],
            any_order=True,
        )

    @patch('django.core.cache.cache.delete_pattern')
    def test_cache_invalidation_on_delete(self, mock_delete_pattern):
        cache.clear()

        self.client.get(
            reverse(self.url_name),
            self._default_params,
        )
        SalesRecord.objects.last().delete()

        mock_delete_pattern.assert_has_calls(
            [
                call('*api_salesrecord_list*'),
                call('*api_salesdataaggregate_list*'),
            ],
            any_order=True,
        )


class AuthenticationTestMixin:
    """
    Mixin to handle common JWT authentication tests for API endpoints that require authentication.
    """

    @property
    def default_params(self):
        return getattr(self, '_default_params', {})

    @property
    def url_name(self):
        raise NotImplementedError(
            '`url_name` property must be set when using `AuthenticationTestMixin`',
        )

    def setUp(self):
        super().setUp()
        self.api_user = User.objects.create_user(username='apiuser', password='apiuserpass')
        self.authenticate()

    def authenticate(self):
        self.token = str(AccessToken.for_user(self.api_user))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_access_denied_without_authentication(self):
        self.client.credentials()
        response = self.client.get(
            reverse(self.url_name),
            self.default_params,
        )
        # we check for 403 not 401, because if JWT fails it falls back to session authentication
        # which is used for the browsable API that returns 403 if user is not an admin
        # TODO: Figure out a way to separate those responses and still check for 401 in this test.
        # Ultimately, just drop browsable API. It only enhances DX.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
