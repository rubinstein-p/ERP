from django.core.exceptions import ValidationError
from django.db import transaction

from core.services import AuditService
from sales.models import Sale, SaleItem


class SaleService:
    """Logica de negocio para operaciones de ventas."""

    @staticmethod
    def _next_sale_number():
        last_sale = Sale.objects.order_by('-id').first()
        next_number = (last_sale.id + 1) if last_sale else 1
        return f"SALE-{next_number:05d}"

    @staticmethod
    def create_sale(customer_name, customer_email, seller, items_data=None, order=None, **extra_fields):
        if not customer_name or not customer_name.strip():
            raise ValidationError('El nombre del cliente es requerido.')

        if not seller or not seller.is_staff:
            raise ValidationError('Solo usuarios staff pueden crear ventas.')

        with transaction.atomic():
            sale = Sale.objects.create(
                sale_number=SaleService._next_sale_number(),
                customer_name=customer_name.strip(),
                customer_email=customer_email or None,
                seller=seller,
                order=order,
                customer_phone=extra_fields.get('customer_phone', ''),
                delivery_date=extra_fields.get('delivery_date') or extra_fields.get('expected_delivery'),
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

                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        product_name=product_name,
                        quantity=item['quantity'],
                        unit_price=unit_price,
                    )

            sale.calculate_totals()

            AuditService.log_action(
                user=seller,
                action='CREATE',
                model_name='Sale',
                object_id=sale.id,
                object_repr=str(sale),
                changes={
                    'sale_number': sale.sale_number,
                    'customer_name': sale.customer_name,
                    'sale_status': sale.sale_status,
                },
                user_agent='',
            )
            return sale

    @staticmethod
    def update_sale_status(sale, new_status, user):
        old_status = sale.sale_status
        sale.sale_status = new_status
        sale.save(update_fields=['sale_status', 'updated_at'])

        AuditService.log_action(
            user=user,
            action='UPDATE',
            model_name='Sale',
            object_id=sale.id,
            object_repr=str(sale),
            changes={'sale_status': {'old': old_status, 'new': new_status}},
            user_agent='',
        )
        return sale

    @staticmethod
    def soft_delete_sale(sale, user):
        sale.is_active = False
        sale.save(update_fields=['is_active', 'updated_at'])

        AuditService.log_action(
            user=user,
            action='DELETE',
            model_name='Sale',
            object_id=sale.id,
            object_repr=str(sale),
            changes={'is_active': {'old': True, 'new': False}},
            user_agent='',
        )
        return sale

    @staticmethod
    def get_sales_by_status(status):
        return Sale.objects.filter(sale_status=status, is_active=True).select_related('seller').order_by('-created_at')

    @staticmethod
    def get_sales_by_customer(customer_email):
        return Sale.objects.filter(customer_email=customer_email, is_active=True).select_related('seller').order_by('-sale_date')
