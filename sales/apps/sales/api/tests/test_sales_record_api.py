import random

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from ...models import SalesRecord
from ..views import PageBasedPagination
from .mixins import AuthenticationTestMixin, SalesRecordAPITestMixin


class SalesRecordAPITest(AuthenticationTestMixin, SalesRecordAPITestMixin, TestCase):
    url_name = 'sales-data-list'

    def setUp(self):
        self.client = APIClient()
        super().setUp()

    def test_list_sales_records_filtered_by_category(self):
        response = self.client.get(
            reverse(self.url_name),
            {
                'category': 'Test Category',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)
        self.assertEqual(response.data['results'][0]['product']['category'], 'Test Category')

    def test_list_filtered_by_date_range(self):
        days_ago = timezone.timedelta(days=random.randint(1, 30))
        for _ in range(100):
            SalesRecord.objects.create(
                product=self.product,
                quantity_sold=5,
                total_sales_amount=self.product.price * 5,
                date_of_sale=timezone.now() - days_ago,
            )

        start_date = (timezone.now() - days_ago).strftime('%Y-%m-%d')
        response = self.client.get(
            reverse(self.url_name),
            {'start_date': start_date},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) > 0)

    def test_list_pagination(self):
        for _ in range(15):
            SalesRecord.objects.create(
                product=self.product,
                quantity_sold=5,
                total_sales_amount=self.product.price * 5,
                date_of_sale=timezone.now(),
            )
        response = self.client.get(
            reverse(self.url_name),
            {'page_size': 10},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIn('next', response.data)

    def test_list_invalid_pagination_parameters(self):
        for _ in range(30):
            SalesRecord.objects.create(
                product=self.product,
                quantity_sold=5,
                total_sales_amount=self.product.price * 5,
                date_of_sale=timezone.now(),
            )
        response = self.client.get(
            reverse(self.url_name),
            {'page_size': -10},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), PageBasedPagination.page_size)

        response = self.client.get(
            reverse(self.url_name),
            {'page': 'invalid'},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
