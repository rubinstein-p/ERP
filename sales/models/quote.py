from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import BaseModel, User


class Quote(BaseModel):
    """Presupuesto de venta. Primer paso del flujo Quote → Order → Sale."""

    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_EXPIRED = 'expired'

    QUOTE_STATUS_CHOICES = [
        (STATUS_DRAFT, 'Borrador'),
        (STATUS_SENT, 'Enviado'),
        (STATUS_APPROVED, 'Aprobado'),
        (STATUS_REJECTED, 'Rechazado'),
        (STATUS_EXPIRED, 'Vencido'),
    ]

    quote_number = models.CharField(max_length=20, unique=True, verbose_name='Número de presupuesto')
    customer_name = models.CharField(max_length=255, verbose_name='Cliente')
    customer_email = models.EmailField(blank=True, null=True, verbose_name='Email del cliente')
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono del cliente')

    quote_date = models.DateField(auto_now_add=True, verbose_name='Fecha de presupuesto')
    valid_until = models.DateField(blank=True, null=True, verbose_name='Válido hasta')

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Subtotal')
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Impuestos')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Total')

    quote_status = models.CharField(
        max_length=20,
        choices=QUOTE_STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name='Estado',
    )

    seller = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='quotes',
        verbose_name='Vendedor',
    )
    notes = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['quote_number']),
            models.Index(fields=['quote_status']),
            models.Index(fields=['customer_email']),
        ]

    def __str__(self):
        return f"Presupuesto {self.quote_number} - {self.customer_name}"

    def clean(self):
        if self.valid_until and self.quote_date and self.valid_until < self.quote_date:
            raise ValidationError({'valid_until': 'La fecha de vencimiento no puede ser anterior a la fecha del presupuesto.'})

    def is_expired(self):
        if self.valid_until:
            return timezone.now().date() > self.valid_until
        return False

    def calculate_totals(self):
        subtotal = sum((item.get_total() for item in self.items.filter(is_active=True)), Decimal('0.00'))
        self.subtotal = subtotal
        self.tax = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
        self.total = (self.subtotal + self.tax).quantize(Decimal('0.01'))
        self.save(update_fields=['subtotal', 'tax', 'total', 'updated_at'])


class QuoteItem(BaseModel):
    """Línea de detalle de un presupuesto."""

    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items', verbose_name='Presupuesto')
    product = models.ForeignKey(
        'masters.Product',
        on_delete=models.PROTECT,
        related_name='quote_items',
        null=True,
        blank=True,
        verbose_name='Producto',
    )
    product_name = models.CharField(max_length=255, verbose_name='Producto')
    quantity = models.PositiveIntegerField(verbose_name='Cantidad')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio unitario')

    class Meta:
        verbose_name = 'Item de presupuesto'
        verbose_name_plural = 'Items de presupuesto'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def get_total(self):
        return (Decimal(self.quantity) * self.unit_price).quantize(Decimal('0.01'))
