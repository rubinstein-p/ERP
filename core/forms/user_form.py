from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
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

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'department', 'employee_id')
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+34 600 000 000'}),
            'employee_id': forms.TextInput(attrs={'placeholder': 'EMP001'}),
        }

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
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'department', 'employee_id', 'is_active')
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+34 600 000 000'}),
            'employee_id': forms.TextInput(attrs={'placeholder': 'EMP001'}),
        }

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