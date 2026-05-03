from decimal import Decimal

from django.core.exceptions import ValidationError

from core.services import AuditService
from masters.models.inventory import Inventory
from masters.models.product import Product


class InventoryService:
    """Gestión de inventario y reservas."""

    @staticmethod
    def get_stock(product):
        """Obtiene cantidad disponible de un producto."""
        try:
            inventory = Inventory.objects.get(product=product)
            return inventory.get_available()
        except Inventory.DoesNotExist:
            return Decimal('0.00')

    @staticmethod
    def reserve(product, quantity, user, reason=''):
        """Reserva cantidad de inventario."""
        if quantity <= 0:
            raise ValidationError('La cantidad a reservar debe ser mayor a cero.')

        try:
            inventory = Inventory.objects.get(product=product)
        except Inventory.DoesNotExist:
            raise ValidationError(f'Producto {product.sku} no tiene inventario registrado.')

        old_reserved = inventory.reserved_quantity
        inventory.reserve(Decimal(str(quantity)))

        AuditService.log_action(
            user=user,
            action='INVENTORY_ADJUST',
            model_name='Inventory',
            object_id=inventory.id,
            object_repr=f"Reserva: {product.sku}",
            changes={
                'action': 'reserve',
                'quantity': str(quantity),
                'reserved_before': str(old_reserved),
                'reserved_after': str(inventory.reserved_quantity),
                'reason': reason,
            },
            user_agent='',
        )
        return inventory

    @staticmethod
    def confirm_reservation(product, quantity, user, reason=''):
        """Confirma reserva (disminuye stock real)."""
        if quantity <= 0:
            raise ValidationError('La cantidad a confirmar debe ser mayor a cero.')

        try:
            inventory = Inventory.objects.get(product=product)
        except Inventory.DoesNotExist:
            raise ValidationError(f'Producto {product.sku} no tiene inventario registrado.')

        old_qty = inventory.quantity
        old_reserved = inventory.reserved_quantity
        inventory.confirm_reservation(Decimal(str(quantity)))

        AuditService.log_action(
            user=user,
            action='INVENTORY_ADJUST',
            model_name='Inventory',
            object_id=inventory.id,
            object_repr=f"Confirmación: {product.sku}",
            changes={
                'action': 'confirm_reservation',
                'quantity': str(quantity),
                'quantity_before': str(old_qty),
                'quantity_after': str(inventory.quantity),
                'reserved_before': str(old_reserved),
                'reserved_after': str(inventory.reserved_quantity),
                'reason': reason,
            },
            user_agent='',
        )
        return inventory

    @staticmethod
    def release_reserved(product, quantity, user, reason=''):
        """Libera reserva (sin cambiar stock)."""
        if quantity <= 0:
            raise ValidationError('La cantidad a liberar debe ser mayor a cero.')

        try:
            inventory = Inventory.objects.get(product=product)
        except Inventory.DoesNotExist:
            raise ValidationError(f'Producto {product.sku} no tiene inventario registrado.')

        old_reserved = inventory.reserved_quantity
        inventory.release_reserved(Decimal(str(quantity)))

        AuditService.log_action(
            user=user,
            action='INVENTORY_ADJUST',
            model_name='Inventory',
            object_id=inventory.id,
            object_repr=f"Liberar reserva: {product.sku}",
            changes={
                'action': 'release_reserved',
                'quantity': str(quantity),
                'reserved_before': str(old_reserved),
                'reserved_after': str(inventory.reserved_quantity),
                'reason': reason,
            },
            user_agent='',
        )
        return inventory

    @staticmethod
    def adjust_stock(product, qty_delta, user, reason=''):
        """Ajusta stock (positivo: entrada, negativo: salida)."""
        if qty_delta == 0:
            raise ValidationError('El ajuste debe ser diferente de cero.')

        try:
            inventory = Inventory.objects.get(product=product)
        except Inventory.DoesNotExist:
            raise ValidationError(f'Producto {product.sku} no tiene inventario registrado.')

        old_qty = inventory.quantity
        inventory.quantity = inventory.quantity + Decimal(str(qty_delta))

        if inventory.quantity < 0:
            raise ValidationError(f'Ajuste generaría cantidad negativa. Disponible: {old_qty}')

        inventory.save(update_fields=['quantity', 'updated_at'])

        AuditService.log_action(
            user=user,
            action='INVENTORY_ADJUST',
            model_name='Inventory',
            object_id=inventory.id,
            object_repr=f"Ajuste: {product.sku}",
            changes={
                'action': 'adjust',
                'delta': str(qty_delta),
                'quantity_before': str(old_qty),
                'quantity_after': str(inventory.quantity),
                'reason': reason,
            },
            user_agent='',
        )
        return inventory
