from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from core.models import User


class UserCreationForm(forms.ModelForm):
    """
    Formulario para la creación de usuarios.
    """
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        help_text="La contraseña debe tener al menos 8 caracteres."
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
        help_text="Repite la contraseña para verificar."
    )
    is_active = forms.BooleanField(label="Activo", required=False, initial=True)
    is_staff = forms.BooleanField(label="Es staff", required=False)
    is_superuser = forms.BooleanField(label="Es superusuario", required=False)
    groups = forms.ModelMultipleChoiceField(
        label="Grupos",
        queryset=Group.objects.none(),
        required=False,
        widget=forms.SelectMultiple,
    )
    user_permissions = forms.ModelMultipleChoiceField(
        label="Permisos directos",
        queryset=Permission.objects.none(),
        required=False,
        widget=forms.SelectMultiple,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'department', 'employee_id')
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+34 600 000 000'}),
            'employee_id': forms.TextInput(attrs={'placeholder': 'EMP001'}),
        }

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_user = request_user
        self.fields['groups'].queryset = Group.objects.order_by('name')
        self.fields['user_permissions'].queryset = Permission.objects.order_by('content_type__app_label', 'codename')

        if not (request_user and request_user.is_superuser):
            self.fields.pop('is_superuser')
            self.fields.pop('user_permissions')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        if password2:
            password_validation.validate_password(password2, self.instance)
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email ya está registrado")
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id and User.objects.filter(employee_id=employee_id).exists():
            raise ValidationError("Este ID de empleado ya existe")
        return employee_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    Formulario para la edición de usuarios.
    """
    groups = forms.ModelMultipleChoiceField(
        label="Grupos",
        queryset=Group.objects.none(),
        required=False,
        widget=forms.SelectMultiple,
    )
    user_permissions = forms.ModelMultipleChoiceField(
        label="Permisos directos",
        queryset=Permission.objects.none(),
        required=False,
        widget=forms.SelectMultiple,
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'phone', 'department', 'employee_id',
            'is_active', 'is_staff', 'is_superuser',
        )
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+34 600 000 000'}),
            'employee_id': forms.TextInput(attrs={'placeholder': 'EMP001'}),
        }

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_user = request_user
        self.fields['groups'].queryset = Group.objects.order_by('name')
        self.fields['groups'].initial = self.instance.groups.all()
        self.fields['user_permissions'].queryset = Permission.objects.order_by('content_type__app_label', 'codename')
        self.fields['user_permissions'].initial = self.instance.user_permissions.all()

        if not (request_user and request_user.is_superuser):
            self.fields.pop('is_superuser')
            self.fields.pop('user_permissions')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este email ya está registrado")
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id and User.objects.filter(employee_id=employee_id).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este ID de empleado ya existe")
        return employee_id


class UserProfileForm(forms.ModelForm):
    """
    Formulario para que los usuarios editen su propio perfil.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'department')
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+34 600 000 000'}),
        }


class PasswordChangeForm(forms.Form):
    """
    Formulario para cambio de contraseña.
    """
    old_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
        help_text="La contraseña debe tener al menos 8 caracteres."
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("La contraseña actual es incorrecta")
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        if password2:
            password_validation.validate_password(password2, self.user)
        return password2

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
        return self.user


class AdminPasswordChangeForm(forms.Form):
    """
    Formulario para que administradores cambien la contraseña de un usuario.
    """
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
        help_text="La contraseña debe tener al menos 8 caracteres."
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        if password2:
            password_validation.validate_password(password2, self.user)
        return password2

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
        return self.user


class LoginForm(forms.Form):
    """
    Formulario de inicio de sesión.
    """
    username = forms.CharField(
        label="Usuario o Email",
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Usuario o email'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
    remember_me = forms.BooleanField(
        required=False,
        label="Recordarme"
    )