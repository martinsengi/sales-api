import random

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from ...models import SalesRecord
from .mixins import AuthenticationTestMixin, SalesRecordAPITestMixin


class SalesDataAggregateAPITest(AuthenticationTestMixin, SalesRecordAPITestMixin, TestCase):
    url_name = 'sales-data-aggregate'
    default_aggregate_by = SalesRecord.AGGREGATE_BY_CHOICES.MONTH

    def setUp(self):
        self.client = APIClient()
        super().setUp()

    def test_required_aggregate_by_parameter(self):
        response = self.client.get(reverse(self.url_name))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_aggregate_by_parameter(self):
        response = self.client.get(
            reverse(self.url_name),
            {'aggregate_by': 'invalid'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_aggregate_sales_by_month(self):
        for _ in range(100):
            quantity_sold = random.randint(1, 10)
            SalesRecord.objects.create(
                product=self.product,
                quantity_sold=quantity_sold,
                total_sales_amount=self.product.price * quantity_sold,
                date_of_sale=timezone.now() - timezone.timedelta(days=random.randint(1, 30)),
            )

        response = self.client.get(
            reverse(self.url_name),
            {'aggregate_by': 'month'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertIn('group', response.data[0])
        self.assertIn('total_sales', response.data[0])

    def test_aggregate_sales_by_category(self):
        for _ in range(100):
            quantity_sold = random.randint(1, 10)
            SalesRecord.objects.create(
                product=self.product,
                quantity_sold=quantity_sold,
                total_sales_amount=self.product.price * quantity_sold,
                date_of_sale=timezone.now() - timezone.timedelta(days=random.randint(1, 30)),
            )

        response = self.client.get(
            reverse(self.url_name),
            {'aggregate_by': 'category'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertIn('group', response.data[0])
        self.assertEquals('Test Category', response.data[0]['group'])
        self.assertIn('total_sales', response.data[0])

    def test_aggregate_sales_with_zero_values(self):
        SalesRecord.objects.create(
            product=self.product,
            quantity_sold=0,
            total_sales_amount=0,
            date_of_sale=timezone.now(),
        )

        response = self.client.get(
            reverse(self.url_name),
            {'aggregate_by': 'category'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertIn('group', response.data[0])
        self.assertIn('total_sales', response.data[0])
        self.assertNotEqual(response.data[0]['average_price'], 0)

    def test_aggregate_sales_with_missing_product(self):
        SalesRecord.objects.create(
            quantity_sold=5,
            total_sales_amount=10,
            date_of_sale=timezone.now(),
            product=None,
        )

        response = self.client.get(reverse(self.url_name), self._default_params)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)

        missing_product_records = [
            record for record in response.data if record.get('product') is None
        ]
        self.assertTrue(len(missing_product_records) > 0)
