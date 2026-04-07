from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models.base import BaseModel


class User(AbstractUser, BaseModel):
    """
    Modelo de usuario personalizado para el ERP.
    Extiende el usuario de Django con campos adicionales.
    """
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Departamento"
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="ID de empleado"
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']

    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"