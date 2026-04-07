from django import forms
from django.core.exceptions import ValidationError
import json

from core.models import SystemParameter


class SystemParameterForm(forms.ModelForm):
    """
    Formulario para la gestión de parámetros del sistema.
    """

    class Meta:
        model = SystemParameter
        fields = ('key', 'value', 'parameter_type', 'description', 'category', 'is_system')
        widgets = {
            'key': forms.TextInput(attrs={'placeholder': 'CLAVE_PARAMETRO'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'category': forms.TextInput(attrs={'placeholder': 'general, finance, security, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es edición, hacer la clave readonly
        if self.instance and self.instance.pk:
            self.fields['key'].disabled = True
            self.fields['parameter_type'].disabled = True

    def clean_key(self):
        key = self.cleaned_data.get('key')
        if key:
            # Convertir a mayúsculas y reemplazar espacios por guiones bajos
            key = key.upper().replace(' ', '_')

            # Verificar que no exista (excepto si es edición)
            if not self.instance.pk:
                if SystemParameter.objects.filter(key=key).exists():
                    raise ValidationError("Ya existe un parámetro con esta clave")

        return key

    def clean_value(self):
        value = self.cleaned_data.get('value')
        param_type = self.cleaned_data.get('parameter_type')

        if param_type and value:
            # Validar según el tipo
            if param_type == 'INTEGER':
                try:
                    int(value)
                except ValueError:
                    raise ValidationError("El valor debe ser un número entero")
            elif param_type == 'DECIMAL':
                try:
                    float(value)
                except ValueError:
                    raise ValidationError("El valor debe ser un número decimal")
            elif param_type == 'BOOLEAN':
                if value.lower() not in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off'):
                    raise ValidationError("El valor debe ser verdadero/falso")
            elif param_type == 'JSON':
                try:
                    json.loads(value)
                except json.JSONDecodeError:
                    raise ValidationError("El valor debe ser un JSON válido")

        return value


class SystemParameterBulkForm(forms.Form):
    """
    Formulario para actualizar múltiples parámetros a la vez.
    """
    parameters = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )

    def clean_parameters(self):
        parameters = self.cleaned_data.get('parameters')
        try:
            data = json.loads(parameters)
            if not isinstance(data, dict):
                raise ValidationError("Formato de parámetros inválido")
            return data
        except json.JSONDecodeError:
            raise ValidationError("Los parámetros deben estar en formato JSON válido")


class ParameterSearchForm(forms.Form):
    """
    Formulario para búsqueda de parámetros.
    """
    search = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Clave, descripción o categoría'})
    )
    category = forms.CharField(
        required=False,
        label="Categoría",
        widget=forms.TextInput(attrs={'placeholder': 'general, finance, etc.'})
    )
    parameter_type = forms.ChoiceField(
        required=False,
        label="Tipo",
        choices=[('', 'Todos')] + list(SystemParameter.PARAMETER_TYPES)
    )
    is_system = forms.NullBooleanField(
        required=False,
        label="Parámetros del sistema"
    )