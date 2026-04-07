from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    Modelo base para todas las entidades del ERP.
    Proporciona campos comunes de auditoría.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.__class__.__name__} {self.pk}"