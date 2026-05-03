from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from sales.models.quote import Quote, QuoteItem
from sales.services.quote_service import QuoteService
from sales.services.order_service import OrderService

User = get_user_model()


class QuoteModelTest(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username='sellerquote',
            email='sellerquote@test.com',
            password='testpass123',
            is_staff=True,
        )

    def test_create_quote(self):
        quote = Quote.objects.create(
            quote_number='QUOT-00001',
            customer_name='Cliente Quote',
            seller=self.seller,
        )
        self.assertEqual(str(quote), 'Presupuesto QUOT-00001 - Cliente Quote')

    def test_calculate_totals(self):
        quote = Quote.objects.create(
            quote_number='QUOT-00002',
            customer_name='Cliente Totales',
            seller=self.seller,
        )
        QuoteItem.objects.create(quote=quote, product_name='Producto', quantity=2, unit_price=Decimal('100.00'))
        quote.calculate_totals()
        self.assertEqual(quote.subtotal, Decimal('200.00'))
        self.assertEqual(quote.tax, Decimal('42.00'))
        self.assertEqual(quote.total, Decimal('242.00'))

    def test_quote_item_get_total(self):
        quote = Quote.objects.create(
            quote_number='QUOT-00003',
            customer_name='Cliente',
            seller=self.seller,
        )
        item = QuoteItem.objects.create(quote=quote, product_name='Item', quantity=3, unit_price=Decimal('10.00'))
        self.assertEqual(item.get_total(), Decimal('30.00'))


class QuoteServiceTest(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staffquote',
            email='staffquote@test.com',
            password='testpass123',
            is_staff=True,
        )
        self.non_staff_user = User.objects.create_user(
            username='normalquote',
            email='normalquote@test.com',
            password='testpass123',
            is_staff=False,
        )

    def test_create_quote_success(self):
        quote = QuoteService.create_quote(
            customer_name='Cliente',
            customer_email='cliente@test.com',
            seller=self.staff_user,
        )
        self.assertIsNotNone(quote.id)
        self.assertTrue(quote.quote_number.startswith('QUOT-'))
        self.assertEqual(quote.quote_status, Quote.STATUS_DRAFT)

    def test_create_quote_non_staff_fails(self):
        with self.assertRaises(ValidationError):
            QuoteService.create_quote(
                customer_name='Cliente',
                customer_email='cliente@test.com',
                seller=self.non_staff_user,
            )

    def test_create_quote_empty_name_fails(self):
        with self.assertRaises(ValidationError):
            QuoteService.create_quote(
                customer_name='   ',
                customer_email='cliente@test.com',
                seller=self.staff_user,
            )

    def test_create_quote_with_items(self):
        quote = QuoteService.create_quote(
            customer_name='Cliente Items',
            customer_email='items@test.com',
            seller=self.staff_user,
            items_data=[
                {'product_name': 'Prod A', 'quantity': 1, 'unit_price': Decimal('100.00')},
            ],
        )
        self.assertEqual(quote.items.count(), 1)
        self.assertEqual(quote.subtotal, Decimal('100.00'))

    def test_update_quote_status(self):
        quote = QuoteService.create_quote(
            customer_name='Cliente Status',
            customer_email='status@test.com',
            seller=self.staff_user,
        )
        updated = QuoteService.update_quote_status(quote, Quote.STATUS_SENT, self.staff_user)
        self.assertEqual(updated.quote_status, Quote.STATUS_SENT)

    def test_convert_to_order(self):
        quote = QuoteService.create_quote(
            customer_name='Cliente Conversion',
            customer_email='conv@test.com',
            seller=self.staff_user,
            items_data=[
                {'product_name': 'Producto', 'quantity': 2, 'unit_price': Decimal('50.00')},
            ],
        )
        order = QuoteService.convert_to_order(quote, self.staff_user)
        self.assertTrue(order.order_number.startswith('ORDER-'))
        self.assertEqual(order.customer_name, quote.customer_name)
        self.assertEqual(order.items.count(), 1)
        quote.refresh_from_db()
        self.assertEqual(quote.quote_status, Quote.STATUS_APPROVED)

    def test_soft_delete_quote(self):
        quote = QuoteService.create_quote(
            customer_name='Cliente Delete',
            customer_email='del@test.com',
            seller=self.staff_user,
        )
        QuoteService.soft_delete_quote(quote, self.staff_user)
        quote.refresh_from_db()
        self.assertFalse(quote.is_active)
