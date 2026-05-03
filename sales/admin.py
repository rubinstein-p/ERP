from django.contrib import admin
from sales.models import Quote, QuoteItem, Order, OrderItem, Sale, SaleItem


# ── Presupuestos ──────────────────────────────────────────────────────────────

class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1
    fields = ('product_name', 'quantity', 'unit_price')


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'customer_name', 'quote_status', 'total', 'valid_until', 'quote_date')
    list_filter = ('quote_status', 'quote_date', 'is_active')
    search_fields = ('quote_number', 'customer_name', 'customer_email')
    readonly_fields = ('quote_number', 'quote_date', 'subtotal', 'tax', 'total', 'created_at', 'updated_at')
    inlines = [QuoteItemInline]

    fieldsets = (
        ('Datos del presupuesto', {'fields': ('quote_number', 'quote_date', 'seller', 'valid_until')}),
        ('Cliente', {'fields': ('customer_name', 'customer_email', 'customer_phone')}),
        ('Montos', {'fields': ('subtotal', 'tax', 'total')}),
        ('Estado', {'fields': ('quote_status',)}),
        ('Observaciones', {'fields': ('notes',)}),
        ('Auditoría', {'fields': ('is_active', 'created_at', 'updated_at')}),
    )


# ── Pedidos ───────────────────────────────────────────────────────────────────

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product_name', 'quantity', 'unit_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'order_status', 'total', 'expected_delivery', 'order_date')
    list_filter = ('order_status', 'order_date', 'is_active')
    search_fields = ('order_number', 'customer_name', 'customer_email')
    readonly_fields = ('order_number', 'order_date', 'subtotal', 'tax', 'total', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    fieldsets = (
        ('Datos del pedido', {'fields': ('order_number', 'order_date', 'seller', 'quote', 'expected_delivery')}),
        ('Cliente', {'fields': ('customer_name', 'customer_email', 'customer_phone')}),
        ('Montos', {'fields': ('subtotal', 'tax', 'total')}),
        ('Estado', {'fields': ('order_status',)}),
        ('Observaciones', {'fields': ('notes',)}),
        ('Auditoría', {'fields': ('is_active', 'created_at', 'updated_at')}),
    )


# ── Ventas ────────────────────────────────────────────────────────────────────

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    fields = ('product_name', 'quantity', 'unit_price')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('sale_number', 'customer_name', 'sale_status', 'payment_status', 'total', 'sale_date')
    list_filter = ('sale_status', 'payment_status', 'sale_date', 'is_active')
    search_fields = ('sale_number', 'customer_name', 'customer_email')
    readonly_fields = ('sale_number', 'sale_date', 'subtotal', 'tax', 'total', 'created_at', 'updated_at')
    inlines = [SaleItemInline]

    fieldsets = (
        ('Datos de venta', {'fields': ('sale_number', 'sale_date', 'seller', 'order')}),
        ('Cliente', {'fields': ('customer_name', 'customer_email', 'customer_phone')}),
        ('Montos', {'fields': ('subtotal', 'tax', 'total')}),
        ('Estado', {'fields': ('sale_status', 'payment_status', 'delivery_date')}),
        ('Observaciones', {'fields': ('notes',)}),
        ('Auditoría', {'fields': ('is_active', 'created_at', 'updated_at')}),
    )
