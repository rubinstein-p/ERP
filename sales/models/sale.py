from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel, User
from sales.models.order import Order


class Sale(BaseModel):
    """Entidad de ventas del ERP."""

    PAYMENT_STATUS_PENDING = 'pending'
    PAYMENT_STATUS_PARTIAL = 'partial'
    PAYMENT_STATUS_PAID = 'paid'
    PAYMENT_STATUS_OVERDUE = 'overdue'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pendiente'),
        (PAYMENT_STATUS_PARTIAL, 'Parcial'),
        (PAYMENT_STATUS_PAID, 'Pagada'),
        (PAYMENT_STATUS_OVERDUE, 'Vencida'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    SALE_STATUS_CHOICES = [
        (STATUS_DRAFT, 'Borrador'),
        (STATUS_CONFIRMED, 'Confirmada'),
        (STATUS_SHIPPED, 'Enviada'),
        (STATUS_DELIVERED, 'Entregada'),
        (STATUS_CANCELLED, 'Cancelada'),
    ]

    sale_number = models.CharField(max_length=20, unique=True, verbose_name='Numero de venta')
    customer_name = models.CharField(max_length=255, verbose_name='Cliente')
    customer_email = models.EmailField(blank=True, null=True, verbose_name='Email del cliente')
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name='Telefono del cliente')

    sale_date = models.DateField(auto_now_add=True, verbose_name='Fecha de venta')
    delivery_date = models.DateField(blank=True, null=True, verbose_name='Fecha de entrega')

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Subtotal')
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Impuestos')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Total')

    sale_status = models.CharField(
        max_length=20,
        choices=SALE_STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name='Estado de la venta',
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_PENDING,
        verbose_name='Estado del pago',
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        related_name='sales',
        null=True,
        blank=True,
        verbose_name='Pedido origen',
    )

    seller = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Vendedor',
    )
    notes = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sale_number']),
            models.Index(fields=['sale_status']),
            models.Index(fields=['customer_email']),
        ]

    def __str__(self):
        return f"Venta {self.sale_number} - {self.customer_name}"

    def clean(self):
        if self.delivery_date and self.sale_date and self.delivery_date < self.sale_date:
            raise ValidationError({'delivery_date': 'La fecha de entrega no puede ser anterior a la fecha de venta.'})

    def calculate_totals(self):
        subtotal = sum((item.get_total() for item in self.items.filter(is_active=True)), Decimal('0.00'))
        self.subtotal = subtotal
        self.tax = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
        self.total = (self.subtotal + self.tax).quantize(Decimal('0.01'))
        self.save(update_fields=['subtotal', 'tax', 'total', 'updated_at'])


class SaleItem(BaseModel):
    """Linea de detalle de una venta."""

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items', verbose_name='Venta')
    product = models.ForeignKey(
        'masters.Product',
        on_delete=models.PROTECT,
        related_name='sale_items',
        null=True,
        blank=True,
        verbose_name='Producto',
    )
    product_name = models.CharField(max_length=255, verbose_name='Producto')
    quantity = models.PositiveIntegerField(verbose_name='Cantidad')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio unitario')

    class Meta:
        verbose_name = 'Item de venta'
        verbose_name_plural = 'Items de venta'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def get_total(self):
        return (Decimal(self.quantity) * self.unit_price).quantize(Decimal('0.01'))
