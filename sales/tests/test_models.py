from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from sales.models import Sale, SaleItem

User = get_user_model()


class SaleModelTest(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123',
            is_staff=True,
        )

    def test_create_sale(self):
        sale = Sale.objects.create(
            sale_number='SALE-00001',
            customer_name='Cliente Test',
            customer_email='cliente@test.com',
            seller=self.seller,
        )
        self.assertEqual(sale.sale_status, Sale.STATUS_DRAFT)
        self.assertEqual(sale.payment_status, Sale.PAYMENT_STATUS_PENDING)
        self.assertTrue(sale.is_active)

    def test_sale_string(self):
        sale = Sale.objects.create(
            sale_number='SALE-00002',
            customer_name='Cliente String',
            seller=self.seller,
        )
        self.assertEqual(str(sale), 'Venta SALE-00002 - Cliente String')

    def test_delivery_date_validation(self):
        sale = Sale(
            sale_number='SALE-00003',
            customer_name='Cliente Fecha',
            seller=self.seller,
            sale_date=timezone.now().date(),
            delivery_date=timezone.now().date() - timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            sale.clean()

    def test_calculate_totals(self):
        sale = Sale.objects.create(
            sale_number='SALE-00004',
            customer_name='Cliente Totales',
            seller=self.seller,
        )
        SaleItem.objects.create(sale=sale, product_name='P1', quantity=2, unit_price=Decimal('100.00'))
        SaleItem.objects.create(sale=sale, product_name='P2', quantity=1, unit_price=Decimal('50.00'))

        sale.calculate_totals()
        sale.refresh_from_db()

        self.assertEqual(sale.subtotal, Decimal('250.00'))
        self.assertEqual(sale.tax, Decimal('52.50'))
        self.assertEqual(sale.total, Decimal('302.50'))


class SaleItemModelTest(TestCase):
    def setUp(self):
        seller = User.objects.create_user(
            username='seller2',
            email='seller2@test.com',
            password='testpass123',
            is_staff=True,
        )
        self.sale = Sale.objects.create(
            sale_number='SALE-00005',
            customer_name='Cliente Item',
            seller=seller,
        )

    def test_item_total(self):
        item = SaleItem.objects.create(
            sale=self.sale,
            product_name='Producto X',
            quantity=3,
            unit_price=Decimal('25.00'),
        )
        self.assertEqual(item.get_total(), Decimal('75.00'))

    def test_cascade_delete_items(self):
        SaleItem.objects.create(
            sale=self.sale,
            product_name='Producto Y',
            quantity=1,
            unit_price=Decimal('10.00'),
        )
        self.sale.delete()
        self.assertEqual(SaleItem.objects.count(), 0)
