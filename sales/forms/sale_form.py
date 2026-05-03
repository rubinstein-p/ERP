from django import forms
from django.core.exceptions import ValidationError

from masters.models import Product
from sales.models import Sale, SaleItem


class SaleForm(forms.ModelForm):
    """Formulario de alta/edicion de ventas."""

    class Meta:
        model = Sale
        fields = ['customer_name', 'customer_email', 'customer_phone', 'delivery_date', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'cliente@email.com'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+54 9 11 1234-5678'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales'}),
        }

    def clean_customer_name(self):
        customer_name = self.cleaned_data.get('customer_name', '').strip()
        if not customer_name:
            raise ValidationError('El nombre del cliente es requerido.')
        return customer_name

    def clean(self):
        cleaned_data = super().clean()
        sale_date = self.instance.sale_date
        delivery_date = cleaned_data.get('delivery_date')

        if sale_date and delivery_date and delivery_date < sale_date:
            self.add_error('delivery_date', 'La fecha de entrega no puede ser anterior a la fecha de venta.')

        return cleaned_data


class SaleItemForm(forms.ModelForm):
    """Formulario para lineas de venta."""

    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Producto',
    )

    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0, 'step': '0.01', 'placeholder': 'Usa precio base si se deja vacío'}
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
            raise ValidationError('La cantidad debe ser mayor a 0.')
        if unit_price is None:
            cleaned_data['unit_price'] = product.base_price
        elif unit_price < 0:
            raise ValidationError('El precio unitario no puede ser negativo.')

        return cleaned_data
