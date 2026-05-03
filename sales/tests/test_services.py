from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from sales.models import Sale
from sales.services import SaleService

User = get_user_model()


class SaleServiceTest(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staffsales',
            email='staffsales@test.com',
            password='testpass123',
            is_staff=True,
        )
        self.non_staff_user = User.objects.create_user(
            username='normalsales',
            email='normalsales@test.com',
            password='testpass123',
            is_staff=False,
        )

    def test_create_sale_success(self):
        sale = SaleService.create_sale(
            customer_name='Cliente Servicio',
            customer_email='cliente.servicio@test.com',
            seller=self.staff_user,
        )
        self.assertIsNotNone(sale.id)
        self.assertTrue(sale.sale_number.startswith('SALE-'))

    def test_create_sale_non_staff_fails(self):
        with self.assertRaises(ValidationError):
            SaleService.create_sale(
                customer_name='Cliente',
                customer_email='cliente@test.com',
                seller=self.non_staff_user,
            )

    def test_create_sale_without_name_fails(self):
        with self.assertRaises(ValidationError):
            SaleService.create_sale(
                customer_name=' ',
                customer_email='cliente@test.com',
                seller=self.staff_user,
            )

    def test_create_sale_with_items_calculates_totals(self):
        sale = SaleService.create_sale(
            customer_name='Cliente Items',
            customer_email='items@test.com',
            seller=self.staff_user,
            items_data=[
                {'product_name': 'Prod A', 'quantity': 2, 'unit_price': Decimal('50.00')},
                {'product_name': 'Prod B', 'quantity': 1, 'unit_price': Decimal('30.00')},
            ],
        )
        sale.refresh_from_db()
        self.assertEqual(sale.items.count(), 2)
        self.assertEqual(sale.subtotal, Decimal('130.00'))

    def test_update_sale_status(self):
        sale = SaleService.create_sale(
            customer_name='Cliente Estado',
            customer_email='estado@test.com',
            seller=self.staff_user,
        )
        SaleService.update_sale_status(sale, Sale.STATUS_CONFIRMED, self.staff_user)
        sale.refresh_from_db()
        self.assertEqual(sale.sale_status, Sale.STATUS_CONFIRMED)

    def test_get_sales_by_status(self):
        sale = SaleService.create_sale(
            customer_name='Cliente Filtro',
            customer_email='filtro@test.com',
            seller=self.staff_user,
        )
        sales = SaleService.get_sales_by_status(Sale.STATUS_DRAFT)
        self.assertIn(sale, sales)

    def test_get_sales_by_customer(self):
        sale = SaleService.create_sale(
            customer_name='Cliente Correo',
            customer_email='correo@test.com',
            seller=self.staff_user,
        )
        sales = SaleService.get_sales_by_customer('correo@test.com')
        self.assertIn(sale, sales)

    def test_soft_delete_sale(self):
        sale = SaleService.create_sale(
            customer_name='Cliente Delete',
            customer_email='delete@test.com',
            seller=self.staff_user,
        )
        SaleService.soft_delete_sale(sale, self.staff_user)
        sale.refresh_from_db()
        self.assertFalse(sale.is_active)
