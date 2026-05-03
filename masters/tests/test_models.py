"""Tests para el módulo de maestros."""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from core.models import User
from masters.models import Category, Supplier, Product, Inventory
from masters.services import ProductService, InventoryService


class CategoryModelTest(TestCase):
    """Tests para modelo Category."""

    def setUp(self):
        self.category = Category.objects.create(name='Electrónica', description='Productos electrónicos')

    def test_create_category(self):
        """Debe crear categoría correctamente."""
        self.assertEqual(self.category.name, 'Electrónica')
        self.assertTrue(self.category.is_active)

    def test_category_slug_generation(self):
        """Debe generar slug automáticamente."""
        self.assertEqual(self.category.slug, 'electronica')

    def test_unique_slug(self):
        """Slug debe ser único."""
        with self.assertRaises(Exception):
            Category.objects.create(name='Electrónica', slug='electronica')

    def test_category_str(self):
        """__str__ debe retornar nombre."""
        self.assertEqual(str(self.category), 'Electrónica')


class SupplierModelTest(TestCase):
    """Tests para modelo Supplier."""

    def setUp(self):
        self.supplier = Supplier.objects.create(
            name='Tech Corp',
            email='contact@techcorp.com',
            phone='+1234567890',
            city='Nueva York',
            country='USA',
        )

    def test_create_supplier(self):
        """Debe crear proveedor correctamente."""
        self.assertEqual(self.supplier.name, 'Tech Corp')
        self.assertTrue(self.supplier.is_active)

    def test_supplier_str(self):
        """__str__ debe retornar nombre."""
        self.assertEqual(str(self.supplier), 'Tech Corp')

    def test_unique_name(self):
        """Nombre debe ser único."""
        with self.assertRaises(Exception):
            Supplier.objects.create(name='Tech Corp')


class ProductModelTest(TestCase):
    """Tests para modelo Product."""

    def setUp(self):
        self.category = Category.objects.create(name='Electrónica')
        self.supplier = Supplier.objects.create(name='Tech Corp')
        self.product = Product.objects.create(
            sku='PROD-001',
            name='Laptop',
            category=self.category,
            supplier=self.supplier,
            base_price=Decimal('999.99'),
        )

    def test_create_product(self):
        """Debe crear producto correctamente."""
        self.assertEqual(self.product.sku, 'PROD-001')
        self.assertEqual(self.product.name, 'Laptop')
        self.assertTrue(self.product.is_active)

    def test_product_str(self):
        """__str__ debe retornar SKU y nombre."""
        self.assertIn('PROD-001', str(self.product))
        self.assertIn('Laptop', str(self.product))

    def test_unique_sku(self):
        """SKU debe ser único."""
        with self.assertRaises(Exception):
            Product.objects.create(sku='PROD-001', name='Otro producto', category=self.category)

    def test_product_clean_invalid_price(self):
        """clean() debe rechazar precio negativo."""
        self.product.base_price = Decimal('-10.00')
        with self.assertRaises(ValidationError):
            self.product.clean()

    def test_product_clean_inactive_category(self):
        """clean() debe rechazar categoría inactiva."""
        self.category.is_active = False
        self.category.save()
        with self.assertRaises(ValidationError):
            self.product.clean()


class InventoryModelTest(TestCase):
    """Tests para modelo Inventory."""

    def setUp(self):
        self.category = Category.objects.create(name='Electrónica')
        self.product = Product.objects.create(
            sku='PROD-001',
            name='Laptop',
            category=self.category,
            base_price=Decimal('999.99'),
        )
        self.inventory = Inventory.objects.create(
            product=self.product,
            quantity=Decimal('100.00'),
            reserved_quantity=Decimal('0.00'),
        )

    def test_create_inventory(self):
        """Debe crear inventario correctamente."""
        self.assertEqual(self.inventory.quantity, Decimal('100.00'))
        self.assertEqual(self.inventory.available_quantity, Decimal('100.00'))

    def test_inventory_available_quantity(self):
        """available_quantity debe ser quantity - reserved_quantity."""
        self.inventory.reserved_quantity = Decimal('30.00')
        self.inventory.save()
        self.assertEqual(self.inventory.available_quantity, Decimal('70.00'))

    def test_inventory_reserve(self):
        """reserve() debe aumentar reserved_quantity."""
        self.inventory.reserve(Decimal('25.00'))
        self.assertEqual(self.inventory.reserved_quantity, Decimal('25.00'))
        self.assertEqual(self.inventory.available_quantity, Decimal('75.00'))

    def test_inventory_reserve_insufficient_stock(self):
        """reserve() debe fallar si no hay stock suficiente."""
        with self.assertRaises(ValidationError):
            self.inventory.reserve(Decimal('150.00'))

    def test_inventory_confirm_reservation(self):
        """confirm_reservation() debe reducir quantity y reserved."""
        self.inventory.reserve(Decimal('30.00'))
        self.inventory.confirm_reservation(Decimal('30.00'))
        self.assertEqual(self.inventory.quantity, Decimal('70.00'))
        self.assertEqual(self.inventory.reserved_quantity, Decimal('0.00'))

    def test_inventory_release_reserved(self):
        """release_reserved() debe reducir reserved sin cambiar quantity."""
        self.inventory.reserve(Decimal('30.00'))
        self.inventory.release_reserved(Decimal('20.00'))
        self.assertEqual(self.inventory.quantity, Decimal('100.00'))
        self.assertEqual(self.inventory.reserved_quantity, Decimal('10.00'))


class ProductServiceTest(TestCase):
    """Tests para ProductService."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='Test1234!',
            is_staff=True,
        )
        self.category = Category.objects.create(name='Electrónica')

    def test_create_product_service(self):
        """Debe crear producto via servicio."""
        product = ProductService.create_product(
            sku='SKU-001',
            name='Producto Test',
            category=self.category,
            base_price=Decimal('100.00'),
            seller=self.user,
        )
        self.assertEqual(product.sku, 'SKU-001')
        self.assertTrue(product.is_active)

    def test_create_product_non_staff(self):
        """create_product debe fallar si user no es staff."""
        non_staff = User.objects.create_user(username='nostaff', password='Test1234!')
        with self.assertRaises(ValidationError):
            ProductService.create_product(
                sku='SKU-002',
                name='Producto',
                category=self.category,
                base_price=Decimal('100.00'),
                seller=non_staff,
            )

    def test_get_product_by_sku(self):
        """Debe obtener producto por SKU."""
        Product.objects.create(sku='SKU-TEST', name='Test', category=self.category)
        product = ProductService.get_by_sku('sku-test')
        self.assertEqual(product.sku, 'SKU-TEST')

    def test_get_available_products(self):
        """get_available_products debe retornar solo activos."""
        Product.objects.create(sku='SKU-001', name='Active', category=self.category)
        prod_inactive = Product.objects.create(sku='SKU-002', name='Inactive', category=self.category, is_active=False)
        activos = ProductService.get_available_products()
        self.assertEqual(activos.count(), 1)
        self.assertNotIn(prod_inactive, activos)

    def test_update_price(self):
        """Debe actualizar precio de producto."""
        product = Product.objects.create(sku='SKU-001', name='Test', category=self.category)
        ProductService.update_price(product, Decimal('250.00'), self.user)
        product.refresh_from_db()
        self.assertEqual(product.base_price, Decimal('250.00'))

    def test_soft_delete_product(self):
        """Debe marcar producto como inactivo."""
        product = Product.objects.create(sku='SKU-001', name='Test', category=self.category)
        ProductService.soft_delete_product(product, self.user)
        product.refresh_from_db()
        self.assertFalse(product.is_active)


class InventoryServiceTest(TestCase):
    """Tests para InventoryService."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Test1234!', is_staff=True)
        self.category = Category.objects.create(name='Electrónica')
        self.product = Product.objects.create(sku='SKU-001', name='Test', category=self.category)
        self.inventory = Inventory.objects.create(product=self.product, quantity=Decimal('100.00'))

    def test_get_stock(self):
        """Debe retornar stock disponible."""
        stock = InventoryService.get_stock(self.product)
        self.assertEqual(stock, Decimal('100.00'))

    def test_reserve(self):
        """Debe reservar stock."""
        InventoryService.reserve(self.product, Decimal('30.00'), self.user, 'Test reserve')
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.reserved_quantity, Decimal('30.00'))

    def test_reserve_insufficient_stock(self):
        """reserve debe fallar si no hay stock."""
        with self.assertRaises(ValidationError):
            InventoryService.reserve(self.product, Decimal('150.00'), self.user)

    def test_confirm_reservation(self):
        """Debe confirmar reserva."""
        InventoryService.reserve(self.product, Decimal('30.00'), self.user)
        InventoryService.confirm_reservation(self.product, Decimal('30.00'), self.user, 'Confirm')
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, Decimal('70.00'))
        self.assertEqual(self.inventory.reserved_quantity, Decimal('0.00'))

    def test_release_reserved(self):
        """Debe liberar reserva."""
        InventoryService.reserve(self.product, Decimal('30.00'), self.user)
        InventoryService.release_reserved(self.product, Decimal('20.00'), self.user)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.reserved_quantity, Decimal('10.00'))

    def test_adjust_stock(self):
        """Debe ajustar stock."""
        InventoryService.adjust_stock(self.product, Decimal('50.00'), self.user, 'Entrada')
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, Decimal('150.00'))

    def test_adjust_stock_negative(self):
        """Debe permitir ajuste negativo si hay stock."""
        InventoryService.adjust_stock(self.product, Decimal('-30.00'), self.user, 'Salida')
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, Decimal('70.00'))
