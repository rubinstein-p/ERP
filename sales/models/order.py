from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel, User
from sales.models.quote import Quote


class Order(BaseModel):
    """Pedido. Segundo paso del flujo Quote → Order → Sale."""

    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_CANCELLED = 'cancelled'

    ORDER_STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_CONFIRMED, 'Confirmado'),
        (STATUS_PROCESSING, 'En proceso'),
        (STATUS_SHIPPED, 'Enviado'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

    order_number = models.CharField(max_length=20, unique=True, verbose_name='Número de pedido')
    quote = models.ForeignKey(
        Quote,
        on_delete=models.PROTECT,
        related_name='orders',
        null=True,
        blank=True,
        verbose_name='Presupuesto origen',
    )
    customer_name = models.CharField(max_length=255, verbose_name='Cliente')
    customer_email = models.EmailField(blank=True, null=True, verbose_name='Email del cliente')
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono del cliente')

    order_date = models.DateField(auto_now_add=True, verbose_name='Fecha de pedido')
    expected_delivery = models.DateField(blank=True, null=True, verbose_name='Entrega estimada')

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Subtotal')
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Impuestos')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Total')

    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Estado',
    )

    seller = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Vendedor',
    )
    notes = models.TextField(blank=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['order_status']),
            models.Index(fields=['customer_email']),
        ]

    def __str__(self):
        return f"Pedido {self.order_number} - {self.customer_name}"

    def clean(self):
        if self.expected_delivery and self.order_date and self.expected_delivery < self.order_date:
            raise ValidationError({'expected_delivery': 'La fecha de entrega estimada no puede ser anterior a la fecha del pedido.'})

    def calculate_totals(self):
        subtotal = sum((item.get_total() for item in self.items.filter(is_active=True)), Decimal('0.00'))
        self.subtotal = subtotal
        self.tax = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
        self.total = (self.subtotal + self.tax).quantize(Decimal('0.01'))
        self.save(update_fields=['subtotal', 'tax', 'total', 'updated_at'])


class OrderItem(BaseModel):
    """Línea de detalle de un pedido."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Pedido')
    product = models.ForeignKey(
        'masters.Product',
        on_delete=models.PROTECT,
        related_name='order_items',
        null=True,
        blank=True,
        verbose_name='Producto',
    )
    product_name = models.CharField(max_length=255, verbose_name='Producto')
    quantity = models.PositiveIntegerField(verbose_name='Cantidad')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio unitario')

    class Meta:
        verbose_name = 'Item de pedido'
        verbose_name_plural = 'Items de pedido'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def get_total(self):
        return (Decimal(self.quantity) * self.unit_price).quantize(Decimal('0.01'))
