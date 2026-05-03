from django.core.exceptions import ValidationError
from django.db import transaction

from core.services import AuditService
from masters.models.product import Product


class ProductService:
    """Lógica de negocio para gestión de productos."""

    @staticmethod
    def create_product(sku, name, category, base_price, seller, supplier=None, description=''):
        """Crea un producto maestro."""
        if not sku or not sku.strip():
            raise ValidationError('SKU es requerido.')

        if not name or not name.strip():
            raise ValidationError('Nombre es requerido.')

        if not seller or not seller.is_staff:
            raise ValidationError('Solo usuarios staff pueden crear productos.')

        if base_price < 0:
            raise ValidationError('El precio base no puede ser negativo.')

        with transaction.atomic():
            product = Product.objects.create(
                sku=sku.strip().upper(),
                name=name.strip(),
                description=description or '',
                category=category,
                supplier=supplier,
                base_price=base_price,
            )
            product.full_clean()
            product.save()

            AuditService.log_action(
                user=seller,
                action='CREATE',
                model_name='Product',
                object_id=product.id,
                object_repr=str(product),
                changes={
                    'sku': product.sku,
                    'name': product.name,
                    'category': str(category),
                },
                user_agent='',
            )
            return product

    @staticmethod
    def get_by_sku(sku):
        """Obtiene producto por SKU."""
        try:
            return Product.objects.get(sku=sku.strip().upper())
        except Product.DoesNotExist:
            raise ValidationError(f'Producto con SKU {sku} no encontrado.')

    @staticmethod
    def get_available_products():
        """Obtiene productos activos."""
        return Product.objects.filter(is_active=True).select_related('category', 'supplier')

    @staticmethod
    def update_price(product, new_price, user):
        """Actualiza precio base del producto."""
        if new_price < 0:
            raise ValidationError('El precio no puede ser negativo.')

        old_price = product.base_price
        product.base_price = new_price
        product.save(update_fields=['base_price', 'updated_at'])

        AuditService.log_action(
            user=user,
            action='UPDATE',
            model_name='Product',
            object_id=product.id,
            object_repr=str(product),
            changes={'base_price': {'old': str(old_price), 'new': str(new_price)}},
            user_agent='',
        )
        return product

    @staticmethod
    def soft_delete_product(product, user):
        """Baja lógica de producto."""
        product.is_active = False
        product.save(update_fields=['is_active', 'updated_at'])

        AuditService.log_action(
            user=user,
            action='DELETE',
            model_name='Product',
            object_id=product.id,
            object_repr=str(product),
            changes={'is_active': {'old': True, 'new': False}},
            user_agent='',
        )
        return product
