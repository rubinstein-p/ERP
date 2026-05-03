from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel
from masters.models.category import Category
from masters.models.supplier import Supplier


class Product(BaseModel):
    """Producto maestro del ERP."""

    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    name = models.CharField(max_length=255, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Categoría',
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='products',
        null=True,
        blank=True,
        verbose_name='Proveedor principal',
    )
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Precio base')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['sku']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['is_active']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"

    def clean(self):
        if not self.category_id:
            raise ValidationError({'category': 'La categoría es requerida.'})
        if not self.category.is_active:
            raise ValidationError({'category': 'La categoría debe estar activa.'})
        if self.supplier and not self.supplier.is_active:
            raise ValidationError({'supplier': 'El proveedor debe estar activo.'})
        if self.base_price < 0:
            raise ValidationError({'base_price': 'El precio base no puede ser negativo.'})
