from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.forms import UserCreationForm, UserChangeForm
from core.models import User, AuditLog, SystemParameter


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Configuración del admin para el modelo de usuario personalizado.
    """
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = ('username', 'email', 'first_name', 'last_name', 'department', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'department', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('phone', 'department', 'employee_id')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('email', 'first_name', 'last_name', 'phone', 'department', 'employee_id')
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Configuración del admin para los logs de auditoría.
    """
    list_display = ('user', 'action', 'model_name', 'object_repr', 'timestamp', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp', 'user')
    search_fields = ('user__username', 'model_name', 'object_repr', 'changes')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'ip_address', 'user_agent', 'timestamp')
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SystemParameter)
class SystemParameterAdmin(admin.ModelAdmin):
    """
    Configuración del admin para los parámetros del sistema.
    """
    list_display = ('key', 'value', 'parameter_type', 'category', 'is_system', 'updated_at')
    list_filter = ('parameter_type', 'category', 'is_system')
    search_fields = ('key', 'description', 'category')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Información básica', {
            'fields': ('key', 'parameter_type', 'value')
        }),
        ('Detalles', {
            'fields': ('description', 'category', 'is_system')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si es edición, hacer key y parameter_type readonly
            return self.readonly_fields + ('key', 'parameter_type')
        return self.readonly_fields
