from django.contrib.auth import get_user_model
from django.test import TestCase

from masters.models import Category, Product
from sales.forms import SaleForm, SaleItemForm
from sales.models import Sale

User = get_user_model()


class SaleFormTest(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username='formseller',
            email='formseller@test.com',
            password='testpass123',
            is_staff=True,
        )

    def test_valid_sale_form(self):
        form = SaleForm(data={
            'customer_name': 'Cliente Form',
            'customer_email': 'cliente.form@test.com',
            'customer_phone': '+54 9 11 0000-0000',
            'notes': 'Notas',
        })
        self.assertTrue(form.is_valid())

    def test_customer_name_required(self):
        form = SaleForm(data={
            'customer_name': ' ',
            'customer_email': 'cliente.form@test.com',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('customer_name', form.errors)

    def test_delivery_date_validation(self):
        sale = Sale.objects.create(
            sale_number='SALE-09999',
            customer_name='Cliente Base',
            seller=self.seller,
        )
        form = SaleForm(
            instance=sale,
            data={
                'customer_name': 'Cliente Base',
                'customer_email': 'cliente.base@test.com',
                'delivery_date': '2000-01-01',
                'customer_phone': '',
                'notes': '',
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_date', form.errors)


class SaleItemFormTest(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Categoria Test')
        self.product = Product.objects.create(
            sku='PRD-TEST-001',
            name='Producto Form Test',
            category=category,
            base_price='100.00',
        )

    def test_valid_item_form(self):
        form = SaleItemForm(data={
            'product': self.product.id,
            'quantity': 3,
            'unit_price': '100.00',
        })
        self.assertTrue(form.is_valid())

    def test_negative_quantity_invalid(self):
        form = SaleItemForm(data={
            'product': self.product.id,
            'quantity': -1,
            'unit_price': '100.00',
        })
        self.assertFalse(form.is_valid())

    def test_negative_price_invalid(self):
        form = SaleItemForm(data={
            'product': self.product.id,
            'quantity': 1,
            'unit_price': '-100.00',
        })
        self.assertFalse(form.is_valid())
