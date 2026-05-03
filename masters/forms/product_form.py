from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from masters.models.product import Product
from masters.models.category import Category
from masters.models.supplier import Supplier


class ProductForm(forms.ModelForm):
    """Formulario para crear/editar productos."""

    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Categoría',
    )
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Proveedor principal',
    )

    class Meta:
        model = Product
        fields = ['sku', 'name', 'description', 'category', 'supplier', 'base_price']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU único'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
        }

    def clean_sku(self):
        sku = self.cleaned_data.get('sku', '').strip().upper()
        if not sku:
            raise ValidationError('SKU es requerido.')
        # Valida que no exista otro producto con el mismo SKU (excepto a sí mismo en ediciones)
        existing = Product.objects.filter(sku=sku).exclude(pk=self.instance.pk).first()
        if existing:
            raise ValidationError('Ya existe un producto con este SKU.')
        return sku

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('El nombre es requerido.')
        return name

    def clean_base_price(self):
        price = self.cleaned_data.get('base_price')
        if price is None:
            price = Decimal('0.00')
        if price < 0:
            raise ValidationError('El precio no puede ser negativo.')
        return price

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category and not category.is_active:
            raise ValidationError('La categoría debe estar activa.')
        return category

    def clean_supplier(self):
        supplier = self.cleaned_data.get('supplier')
        if supplier and not supplier.is_active:
            raise ValidationError('El proveedor debe estar activo.')
        return supplier
