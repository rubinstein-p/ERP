from django.db import models

from core.models.base import BaseModel


class SystemParameter(BaseModel):
    """
    Modelo para parámetros configurables del sistema ERP.
    """
    PARAMETER_TYPES = [
        ('STRING', 'Texto'),
        ('INTEGER', 'Número entero'),
        ('DECIMAL', 'Número decimal'),
        ('BOOLEAN', 'Verdadero/Falso'),
        ('DATE', 'Fecha'),
        ('JSON', 'JSON'),
    ]

    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Clave"
    )
    value = models.TextField(
        verbose_name="Valor"
    )
    parameter_type = models.CharField(
        max_length=20,
        choices=PARAMETER_TYPES,
        default='STRING',
        verbose_name="Tipo de parámetro"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Categoría"
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name="Parámetro del sistema"
    )

    class Meta:
        verbose_name = "Parámetro del sistema"
        verbose_name_plural = "Parámetros del sistema"
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.key}: {self.value}"