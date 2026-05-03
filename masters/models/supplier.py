from django.db import models

from core.models import BaseModel


class Supplier(BaseModel):
    """Proveedor de productos."""

    name = models.CharField(max_length=255, unique=True, verbose_name='Nombre')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    address = models.CharField(max_length=255, blank=True, verbose_name='Dirección')
    city = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
    country = models.CharField(max_length=100, blank=True, verbose_name='País')

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name
