from django import forms
from django.core.exceptions import ValidationError

from masters.models.supplier import Supplier


class SupplierForm(forms.ModelForm):
    """Formulario para crear/editar proveedores."""

    class Meta:
        model = Supplier
        fields = ['name', 'email', 'phone', 'address', 'city', 'country']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'País'}),
        }

    def clean_name(self):
        raw_name = self.cleaned_data.get('name')
        name = (raw_name or '').strip()
        if not name:
            raise ValidationError('El nombre es requerido.')
        return name

    def clean_email(self):
        raw_email = self.cleaned_data.get('email')
        email = (raw_email or '').strip() or None
        if email:
            existing = Supplier.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing:
                raise ValidationError('Este email ya está registrado.')
        return email
