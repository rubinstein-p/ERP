from django import forms
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError

from core.services import RoleService


class RoleForm(forms.ModelForm):
    """
    Formulario para alta/edicion de roles (grupos).
    """

    permissions = forms.ModelMultipleChoiceField(
        label="Permisos",
        queryset=Permission.objects.order_by('content_type__app_label', 'codename'),
        required=False,
        widget=forms.SelectMultiple,
    )
    permission_modules = forms.MultipleChoiceField(
        label="Modulos para matriz rapida",
        required=False,
        choices=(),
        widget=forms.SelectMultiple,
        help_text='Selecciona uno o mas modulos para autocompletar permisos.',
    )
    permission_level = forms.ChoiceField(
        label='Nivel de acceso',
        required=False,
        choices=RoleService.ACCESS_LEVEL_CHOICES,
        initial='operate',
        help_text='Se aplica sobre los modulos seleccionados en la matriz rapida.',
    )

    class Meta:
        model = Group
        fields = ('name', 'permissions')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permission_modules'].choices = RoleService.get_module_choices()

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        qs = Group.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ya existe un rol con ese nombre')
        return name

    def clean(self):
        cleaned_data = super().clean()
        selected_modules = cleaned_data.get('permission_modules') or []
        access_level = cleaned_data.get('permission_level') or 'operate'
        selected_permissions = cleaned_data.get('permissions')

        if selected_modules:
            matrix_permissions = RoleService.permissions_for_modules(selected_modules, access_level=access_level)
            matrix_permission_ids = set(matrix_permissions.values_list('id', flat=True))

            if selected_permissions is not None:
                selected_permission_ids = set(selected_permissions.values_list('id', flat=True))
            else:
                selected_permission_ids = set()

            final_ids = selected_permission_ids.union(matrix_permission_ids)
            cleaned_data['permissions'] = Permission.objects.filter(id__in=final_ids)

        return cleaned_data
