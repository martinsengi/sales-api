from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from sales.apps.products.models import Product

from .interfaces import ProductSnapshot
from .models import SalesRecord


class SalesRecordModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Test Product',
            category='Electronics',
            price=99.99,
        )

    def test_create_sales_record(self):
        sales_record = SalesRecord.objects.create(
            product=self.product,
            quantity_sold=5,
            total_sales_amount=500.00,
            date_of_sale=timezone.now(),
        )
        self.assertEqual(sales_record.product, self.product)
        self.assertEqual(sales_record.quantity_sold, 5)
        self.assertEqual(sales_record.total_sales_amount, 500.00)

    def test_sales_record_str(self):
        sales_record = SalesRecord(
            product=self.product,
            quantity_sold=5,
            total_sales_amount=250.00,
        )
        self.assertEqual(str(sales_record), f'{self.product.name} {sales_record.id}')

    def test_invalid_quantity_sold(self):
        sales_record = SalesRecord(
            product=self.product,
            quantity_sold=-5,
            total_sales_amount=500.00,
        )
        with self.assertRaises(ValidationError):
            sales_record.full_clean()

    def test_invalid_total_amount(self):
        sales_record = SalesRecord(
            product=self.product,
            quantity_sold=5,
            total_sales_amount=-500.00,
        )
        with self.assertRaises(ValidationError):
            sales_record.full_clean()

    def test_product_snapshot_stored(self):
        sales_record = SalesRecord.objects.create(
            product=self.product,
            quantity_sold=5,
            total_sales_amount=500.00,
            date_of_sale=timezone.now(),
        )
        expected_snapshot = ProductSnapshot(
            name=self.product.name,
            category=self.product.category,
            price=str(self.product.price),
        )
        self.assertEqual(sales_record.product_snapshot, expected_snapshot)

    def test_aggregate_by_month(self):
        date_of_sale = timezone.now()
        SalesRecord.objects.create(
            product=self.product,
            quantity_sold=5,
            total_sales_amount=250.00,
            date_of_sale=date_of_sale,
        )
        SalesRecord.objects.create(
            product=self.product,
            quantity_sold=15,
            total_sales_amount=750.00,
            date_of_sale=date_of_sale,
        )
        aggregated_data = SalesRecord.get_data_aggregated_queryset(
            aggregate_by=SalesRecord.AggregateByChoices.MONTH
        )
        self.assertEqual(aggregated_data[0]['total_sales'], 1000.00)
        self.assertEqual(aggregated_data[0]['average_price'], 50.00)

    def test_aggregate_by_category(self):
        date_of_sale = timezone.now()
        SalesRecord.objects.create(
            product=self.product,
            quantity_sold=5,
            total_sales_amount=250.00,
            date_of_sale=date_of_sale,
        )
        SalesRecord.objects.create(
            product=self.product,
            quantity_sold=15,
            total_sales_amount=750.00,
            date_of_sale=date_of_sale,
        )
        aggregated_data = SalesRecord.get_data_aggregated_queryset(
            aggregate_by=SalesRecord.AggregateByChoices.CATEGORY
        )
        self.assertEqual(aggregated_data[0]['group'], 'Electronics')
        self.assertEqual(aggregated_data[0]['total_sales'], 1000.00)
        self.assertEqual(aggregated_data[0]['average_price'], 50.00)
