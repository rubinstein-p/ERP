from django.test import TestCase

from masters.forms import ProductForm, SupplierForm
from masters.models import Category, Supplier


class SupplierFormTest(TestCase):
    def test_clean_email_accepts_none_without_crashing(self):
        form = SupplierForm(
            data={
                'name': 'Proveedor Demo',
                'email': None,
                'phone': '123',
                'address': 'Calle 1',
                'city': 'Ciudad',
                'country': 'Pais',
            }
        )
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data['email'])

    def test_clean_email_rejects_duplicate_email(self):
        Supplier.objects.create(name='Proveedor 1', email='dup@test.com')
        form = SupplierForm(
            data={
                'name': 'Proveedor 2',
                'email': 'dup@test.com',
                'phone': '',
                'address': '',
                'city': '',
                'country': '',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class ProductFormTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronica')

    def test_missing_category_returns_validation_error(self):
        form = ProductForm(
            data={
                'sku': 'PRD-001',
                'name': 'Producto Demo',
                'description': 'Desc',
                'supplier': '',
                'base_price': '100.00',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)
