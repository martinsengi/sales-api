from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Product


class ProductModelTest(TestCase):

    def test_create_product(self):
        product = Product.objects.create(
            name='Test Product',
            category='Test Product Category',
            price=99.99,
        )
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.category, 'Test Product Category')
        self.assertEqual(product.price, 99.99)

    def test_price_is_positive(self):
        product = Product(
            name='Test Product',
            price=-50.00,
        )
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_str_method(self):
        product = Product(
            name='Test Product',
            price=-50.00,
        )
        self.assertEqual(str(product), 'Test Product')
