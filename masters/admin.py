from django.contrib import admin

from masters.models import Category, Supplier, Product, Inventory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    fieldsets = (
        ('Información', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'country', 'created_at']
    search_fields = ['name', 'email', 'phone']
    fieldsets = (
        ('Información', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Ubicación', {
            'fields': ('address', 'city', 'country')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'supplier', 'base_price', 'is_active']
    list_filter = ['is_active', 'category', 'supplier', 'created_at']
    search_fields = ['sku', 'name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información', {
            'fields': ('sku', 'name', 'description')
        }),
        ('Clasificación', {
            'fields': ('category', 'supplier')
        }),
        ('Precios', {
            'fields': ('base_price',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'reserved_quantity', 'available_quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__sku', 'product__name']
    readonly_fields = ['created_at', 'updated_at', 'available_quantity']
    fieldsets = (
        ('Producto', {
            'fields': ('product',)
        }),
        ('Stock', {
            'fields': ('quantity', 'reserved_quantity', 'available_quantity')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def available_quantity(self, obj):
        return obj.get_available()
    available_quantity.short_description = 'Disponible'

