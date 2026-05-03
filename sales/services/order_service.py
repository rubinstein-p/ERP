from django.core.exceptions import ValidationError
from django.db import transaction

from core.services import AuditService
from sales.models.order import Order, OrderItem


class OrderService:
    """Lógica de negocio para pedidos."""

    @staticmethod
    def _next_order_number():
        last = Order.objects.order_by('-id').first()
        next_number = (last.id + 1) if last else 1
        return f"ORDER-{next_number:05d}"

    @staticmethod
    def create_order(customer_name, customer_email, seller, items_data=None, quote=None, **extra_fields):
        if not customer_name or not customer_name.strip():
            raise ValidationError('El nombre del cliente es requerido.')

        if not seller or not seller.is_staff:
            raise ValidationError('Solo usuarios staff pueden crear pedidos.')

        with transaction.atomic():
            order = Order.objects.create(
                order_number=OrderService._next_order_number(),
                customer_name=customer_name.strip(),
                customer_email=customer_email or None,
                seller=seller,
                quote=quote,
                customer_phone=extra_fields.get('customer_phone', ''),
                expected_delivery=extra_fields.get('expected_delivery'),
                notes=extra_fields.get('notes', ''),
            )

            if items_data:
                for item in items_data:
                    product = item.get('product')
                    product_name = (item.get('product_name') or '').strip()
                    unit_price = item.get('unit_price')

                    if product is not None:
                        product_name = product.name
                        if unit_price is None:
                            unit_price = product.base_price

                    if not product_name:
                        raise ValidationError('Cada ítem debe tener un producto válido.')

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product_name,
                        quantity=item['quantity'],
                        unit_price=unit_price,
                    )

            order.calculate_totals()

            AuditService.log_action(
                user=seller,
                action='CREATE',
                model_name='Order',
                object_id=order.id,
                object_repr=str(order),
                changes={
                    'order_number': order.order_number,
                    'customer_name': order.customer_name,
                    'order_status': order.order_status,
                },
                user_agent='',
            )
            return order

    @staticmethod
    def update_order_status(order, new_status, user):
        old_status = order.order_status
        order.order_status = new_status
        order.save(update_fields=['order_status', 'updated_at'])

        AuditService.log_action(
            user=user,
            action='UPDATE',
            model_name='Order',
            object_id=order.id,
            object_repr=str(order),
            changes={'order_status': {'old': old_status, 'new': new_status}},
            user_agent='',
        )
        return order

    @staticmethod
    def convert_to_sale(order, user):
        """Convierte un pedido confirmado en una venta."""
        from sales.services.sale_service import SaleService

        if order.order_status not in (Order.STATUS_PENDING, Order.STATUS_CONFIRMED, Order.STATUS_PROCESSING):
            raise ValidationError('Solo se pueden convertir pedidos en estado Pendiente, Confirmado o En proceso.')

        with transaction.atomic():
            items_data = [
                {
                    'product': item.product,
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                }
                for item in order.items.filter(is_active=True)
            ]

            sale = SaleService.create_sale(
                customer_name=order.customer_name,
                customer_email=order.customer_email,
                seller=user,
                order=order,
                items_data=items_data,
                customer_phone=order.customer_phone,
                expected_delivery=order.expected_delivery,
                notes=order.notes,
            )

            order.order_status = Order.STATUS_CONFIRMED
            order.save(update_fields=['order_status', 'updated_at'])

            AuditService.log_action(
                user=user,
                action='UPDATE',
                model_name='Order',
                object_id=order.id,
                object_repr=str(order),
                changes={'converted_to_sale': sale.sale_number},
                user_agent='',
            )
            return sale

    @staticmethod
    def soft_delete_order(order, user):
        order.is_active = False
        order.save(update_fields=['is_active', 'updated_at'])

        AuditService.log_action(
            user=user,
            action='DELETE',
            model_name='Order',
            object_id=order.id,
            object_repr=str(order),
            changes={'is_active': {'old': True, 'new': False}},
            user_agent='',
        )
        return order

    @staticmethod
    def get_orders_by_status(status):
        return Order.objects.filter(order_status=status, is_active=True).select_related('seller').order_by('-created_at')
