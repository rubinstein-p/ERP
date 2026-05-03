from django import forms
from django.core.exceptions import ValidationError

from masters.models import Product
from sales.models.order import Order, OrderItem


class OrderForm(forms.ModelForm):
    """Formulario de alta/edición de pedidos."""

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'customer_phone', 'expected_delivery', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'cliente@email.com'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+54 9 11 1234-5678'}),
            'expected_delivery': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales'}),
        }

    def clean_customer_name(self):
        name = self.cleaned_data.get('customer_name', '').strip()
        if not name:
            raise ValidationError('El nombre del cliente es requerido.')
        return name


class OrderItemForm(forms.ModelForm):
    """Formulario para líneas de pedido."""

    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Producto',
    )

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'placeholder': 'Usa precio base si se deja vacío'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')

        if not product:
            raise ValidationError({'product': 'Debe seleccionar un producto.'})

        cleaned_data['product_name'] = product.name

        if quantity is not None and quantity <= 0:
            raise ValidationError({'quantity': 'La cantidad debe ser mayor a cero.'})
        if unit_price is None:
            cleaned_data['unit_price'] = product.base_price
        elif unit_price < 0:
            raise ValidationError({'unit_price': 'El precio unitario no puede ser negativo.'})
        return cleaned_data
