from django.db import models

from core.models.base import BaseModel
from core.models.user import User


class AuditLog(BaseModel):
    """
    Modelo para registrar todas las operaciones de auditoría del sistema.
    """
    ACTION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('VIEW', 'Visualización'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Acción"
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name="Modelo"
    )
    object_id = models.PositiveIntegerField(
        verbose_name="ID del objeto"
    )
    object_repr = models.TextField(
        verbose_name="Representación del objeto"
    )
    changes = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Cambios realizados"
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="Dirección IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora"
    )

    class Meta:
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} {self.object_id}"