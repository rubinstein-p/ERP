from django import forms
from django.core.exceptions import ValidationError

from masters.models.category import Category


class CategoryForm(forms.ModelForm):
    """Formulario para crear/editar categorías."""

    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('El nombre es requerido.')
        return name
