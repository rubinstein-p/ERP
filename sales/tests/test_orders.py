from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from sales.models.order import Order, OrderItem
from sales.models.quote import Quote
from sales.services.order_service import OrderService
from sales.services.quote_service import QuoteService

User = get_user_model()


class OrderModelTest(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            username='sellerorder',
            email='sellerorder@test.com',
            password='testpass123',
            is_staff=True,
        )

    def test_create_order(self):
        order = Order.objects.create(
            order_number='ORDER-00001',
            customer_name='Cliente Order',
            seller=self.seller,
        )
        self.assertEqual(str(order), 'Pedido ORDER-00001 - Cliente Order')

    def test_calculate_totals(self):
        order = Order.objects.create(
            order_number='ORDER-00002',
            customer_name='Cliente Totales',
            seller=self.seller,
        )
        OrderItem.objects.create(order=order, product_name='Producto', quantity=3, unit_price=Decimal('100.00'))
        order.calculate_totals()
        self.assertEqual(order.subtotal, Decimal('300.00'))
        self.assertEqual(order.tax, Decimal('63.00'))
        self.assertEqual(order.total, Decimal('363.00'))

    def test_order_item_get_total(self):
        order = Order.objects.create(
            order_number='ORDER-00003',
            customer_name='Cliente',
            seller=self.seller,
        )
        item = OrderItem.objects.create(order=order, product_name='Item', quantity=4, unit_price=Decimal('25.00'))
        self.assertEqual(item.get_total(), Decimal('100.00'))


class OrderServiceTest(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='stafforder',
            email='stafforder@test.com',
            password='testpass123',
            is_staff=True,
        )
        self.non_staff_user = User.objects.create_user(
            username='normalorder',
            email='normalorder@test.com',
            password='testpass123',
            is_staff=False,
        )

    def test_create_order_success(self):
        order = OrderService.create_order(
            customer_name='Cliente',
            customer_email='cliente@test.com',
            seller=self.staff_user,
        )
        self.assertIsNotNone(order.id)
        self.assertTrue(order.order_number.startswith('ORDER-'))
        self.assertEqual(order.order_status, Order.STATUS_PENDING)

    def test_create_order_non_staff_fails(self):
        with self.assertRaises(ValidationError):
            OrderService.create_order(
                customer_name='Cliente',
                customer_email='cliente@test.com',
                seller=self.non_staff_user,
            )

    def test_create_order_empty_name_fails(self):
        with self.assertRaises(ValidationError):
            OrderService.create_order(
                customer_name='   ',
                customer_email='cliente@test.com',
                seller=self.staff_user,
            )

    def test_create_order_with_items(self):
        order = OrderService.create_order(
            customer_name='Cliente Items',
            customer_email='items@test.com',
            seller=self.staff_user,
            items_data=[
                {'product_name': 'Prod A', 'quantity': 2, 'unit_price': Decimal('50.00')},
            ],
        )
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.subtotal, Decimal('100.00'))

    def test_create_order_from_quote(self):
        quote = QuoteService.create_quote(
            customer_name='Cliente Quote',
            customer_email='quote@test.com',
            seller=self.staff_user,
        )
        order = OrderService.create_order(
            customer_name='Cliente Quote',
            customer_email='quote@test.com',
            seller=self.staff_user,
            quote=quote,
        )
        self.assertEqual(order.quote, quote)

    def test_update_order_status(self):
        order = OrderService.create_order(
            customer_name='Cliente Status',
            customer_email='status@test.com',
            seller=self.staff_user,
        )
        updated = OrderService.update_order_status(order, Order.STATUS_CONFIRMED, self.staff_user)
        self.assertEqual(updated.order_status, Order.STATUS_CONFIRMED)

    def test_convert_to_sale(self):
        order = OrderService.create_order(
            customer_name='Cliente Conversion',
            customer_email='conv@test.com',
            seller=self.staff_user,
            items_data=[
                {'product_name': 'Producto', 'quantity': 1, 'unit_price': Decimal('200.00')},
            ],
        )
        sale = OrderService.convert_to_sale(order, self.staff_user)
        self.assertTrue(sale.sale_number.startswith('SALE-'))
        self.assertEqual(sale.customer_name, order.customer_name)
        self.assertEqual(sale.order, order)
        self.assertEqual(sale.items.count(), 1)
        order.refresh_from_db()
        self.assertEqual(order.order_status, Order.STATUS_CONFIRMED)

    def test_soft_delete_order(self):
        order = OrderService.create_order(
            customer_name='Cliente Delete',
            customer_email='del@test.com',
            seller=self.staff_user,
        )
        OrderService.soft_delete_order(order, self.staff_user)
        order.refresh_from_db()
        self.assertFalse(order.is_active)
