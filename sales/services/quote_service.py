from django.core.exceptions import ValidationError
from django.db import transaction

from core.services import AuditService
from sales.models.quote import Quote, QuoteItem


class QuoteService:
    """Lógica de negocio para presupuestos."""

    @staticmethod
    def _next_quote_number():
        last = Quote.objects.order_by('-id').first()
        next_number = (last.id + 1) if last else 1
        return f"QUOT-{next_number:05d}"

    @staticmethod
    def create_quote(customer_name, customer_email, seller, items_data=None, **extra_fields):
        if not customer_name or not customer_name.strip():
            raise ValidationError('El nombre del cliente es requerido.')

        if not seller or not seller.is_staff:
            raise ValidationError('Solo usuarios staff pueden crear presupuestos.')

        with transaction.atomic():
            quote = Quote.objects.create(
                quote_number=QuoteService._next_quote_number(),
                customer_name=customer_name.strip(),
                customer_email=customer_email or None,
                seller=seller,
                customer_phone=extra_fields.get('customer_phone', ''),
                valid_until=extra_fields.get('valid_until'),
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

                    QuoteItem.objects.create(
                        quote=quote,
                        product=product,
                        product_name=product_name,
                        quantity=item['quantity'],
                        unit_price=unit_price,
                    )

            quote.calculate_totals()

            AuditService.log_action(
                user=seller,
                action='CREATE',
                model_name='Quote',
                object_id=quote.id,
                object_repr=str(quote),
                changes={
                    'quote_number': quote.quote_number,
                    'customer_name': quote.customer_name,
                    'quote_status': quote.quote_status,
                },
                user_agent='',
            )
            return quote

    @staticmethod
    def update_quote_status(quote, new_status, user):
        old_status = quote.quote_status
        quote.quote_status = new_status
        quote.save(update_fields=['quote_status', 'updated_at'])

        AuditService.log_action(
            user=user,
            action='UPDATE',
            model_name='Quote',
            object_id=quote.id,
            object_repr=str(quote),
            changes={'quote_status': {'old': old_status, 'new': new_status}},
            user_agent='',
        )
        return quote

    @staticmethod
    def convert_to_order(quote, user):
        """Convierte un presupuesto aprobado en un pedido."""
        from sales.services.order_service import OrderService

        if quote.quote_status not in (Quote.STATUS_DRAFT, Quote.STATUS_SENT, Quote.STATUS_APPROVED):
            raise ValidationError('Solo se pueden convertir presupuestos en estado Borrador, Enviado o Aprobado.')

        with transaction.atomic():
            items_data = [
                {
                    'product': item.product,
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                }
                for item in quote.items.filter(is_active=True)
            ]

            order = OrderService.create_order(
                customer_name=quote.customer_name,
                customer_email=quote.customer_email,
                seller=user,
                quote=quote,
                items_data=items_data,
                customer_phone=quote.customer_phone,
                notes=quote.notes,
            )

            quote.quote_status = Quote.STATUS_APPROVED
            quote.save(update_fields=['quote_status', 'updated_at'])

            AuditService.log_action(
                user=user,
                action='UPDATE',
                model_name='Quote',
                object_id=quote.id,
                object_repr=str(quote),
                changes={'converted_to_order': order.order_number},
                user_agent='',
            )
            return order

    @staticmethod
    def soft_delete_quote(quote, user):
        quote.is_active = False
        quote.save(update_fields=['is_active', 'updated_at'])

        AuditService.log_action(
            user=user,
            action='DELETE',
            model_name='Quote',
            object_id=quote.id,
            object_repr=str(quote),
            changes={'is_active': {'old': True, 'new': False}},
            user_agent='',
        )
        return quote

    @staticmethod
    def get_quotes_by_status(status):
        return Quote.objects.filter(quote_status=status, is_active=True).select_related('seller').order_by('-created_at')
