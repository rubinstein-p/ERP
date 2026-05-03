from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel
from masters.models.product import Product


class Inventory(BaseModel):
    """Gestión de inventario por producto."""

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name='Producto',
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Cantidad disponible')
    reserved_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Cantidad reservada')

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'

    def __str__(self):
        return f"Inventario {self.product.sku}"

    @property
    def available_quantity(self):
        """Cantidad disponible (sin reservas)."""
        return self.quantity - self.reserved_quantity

    def clean(self):
        if self.quantity < 0:
            raise ValidationError({'quantity': 'La cantidad no puede ser negativa.'})
        if self.reserved_quantity < 0:
            raise ValidationError({'reserved_quantity': 'La cantidad reservada no puede ser negativa.'})
        if self.reserved_quantity > self.quantity:
            raise ValidationError({'reserved_quantity': 'La cantidad reservada no puede superar la cantidad disponible.'})

    def get_available(self):
        """Retorna cantidad disponible (alias para property)."""
        return self.available_quantity

    def reserve(self, qty):
        """Reserva cantidad especificada."""
        if qty <= 0:
            raise ValidationError('La cantidad a reservar debe ser mayor a cero.')
        if qty > self.available_quantity:
            raise ValidationError(
                f'Stock insuficiente. Disponible: {self.available_quantity}, Solicitado: {qty}'
            )
        self.reserved_quantity = (self.reserved_quantity + Decimal(str(qty))).quantize(Decimal('0.01'))
        self.save(update_fields=['reserved_quantity', 'updated_at'])

    def confirm_reservation(self, qty):
        """Confirma reserva (disminuye qty real)."""
        if qty <= 0:
            raise ValidationError('La cantidad a confirmar debe ser mayor a cero.')
        if qty > self.reserved_quantity:
            raise ValidationError(f'Cantidad reservada insuficiente. Reservado: {self.reserved_quantity}, Solicitado: {qty}')
        self.quantity = (self.quantity - Decimal(str(qty))).quantize(Decimal('0.01'))
        self.reserved_quantity = (self.reserved_quantity - Decimal(str(qty))).quantize(Decimal('0.01'))
        self.save(update_fields=['quantity', 'reserved_quantity', 'updated_at'])

    def release_reserved(self, qty):
        """Libera reserva (sin cambiar qty)."""
        if qty <= 0:
            raise ValidationError('La cantidad a liberar debe ser mayor a cero.')
        if qty > self.reserved_quantity:
            raise ValidationError(f'Cantidad reservada insuficiente. Reservado: {self.reserved_quantity}, Solicitado: {qty}')
        self.reserved_quantity = (self.reserved_quantity - Decimal(str(qty))).quantize(Decimal('0.01'))
        self.save(update_fields=['reserved_quantity', 'updated_at'])
