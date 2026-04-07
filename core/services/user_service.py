from django.contrib.auth import authenticate
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.conf import settings

from core.models import User, AuditLog


class UserService:
    """
    Servicio para la gestión de usuarios y autenticación.
    Maneja toda la lógica de negocio relacionada con usuarios.
    """

    @staticmethod
    def create_user(username, email, password, **extra_fields):
        """
        Crea un nuevo usuario con validaciones adicionales.

        Args:
            username (str): Nombre de usuario único
            email (str): Email del usuario
            password (str): Contraseña
            **extra_fields: Campos adicionales

        Returns:
            User: Instancia del usuario creado

        Raises:
            ValidationError: Si hay errores de validación
        """
        if User.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya existe")

        if User.objects.filter(email=email).exists():
            raise ValidationError("El email ya está registrado")

        created_by = extra_fields.pop('created_by', None)
        groups = extra_fields.pop('groups', None)
        user_permissions = extra_fields.pop('user_permissions', None)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )

        if groups is not None:
            user.groups.set(groups)

        if user_permissions is not None:
            user.user_permissions.set(user_permissions)

        # Registrar en auditoría
        AuditLog.objects.create(
            user=created_by or user,
            action='CREATE',
            model_name='User',
            object_id=user.id,
            object_repr=str(user),
            changes={
                'action': 'user_created',
                'groups': list(user.groups.values_list('name', flat=True)),
                'permissions_count': user.user_permissions.count(),
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            }
        )

        return user

    @staticmethod
    def _get_client_ip(request):
        if not request:
            return None
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    @staticmethod
    def _rate_limit_keys(identifier, ip_address):
        normalized = (identifier or '').strip().lower()
        keys = [f'login_attempts:id:{normalized}']
        if ip_address:
            keys.append(f'login_attempts:ip:{ip_address}')
        return keys

    @staticmethod
    def _log_login_failed(identifier, request=None, reason='invalid_credentials', remaining=None):
        user_lookup = User.objects.filter(username__iexact=identifier).first()
        if not user_lookup and '@' in (identifier or ''):
            user_lookup = User.objects.filter(email__iexact=identifier).first()

        ip_address = UserService._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''

        AuditLog.objects.create(
            user=user_lookup,
            action='LOGIN_FAILED',
            model_name='UserAuth',
            object_id=user_lookup.id if user_lookup else 0,
            object_repr=identifier or 'unknown_identifier',
            changes={
                'reason': reason,
                'remaining_attempts': remaining,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def authenticate_user(identifier, password, request=None, return_detail=False):
        """
        Autentica un usuario por nombre de usuario o email.

        Args:
            identifier (str): Nombre de usuario o email
            password (str): Contraseña

        Returns:
            User or None: Usuario autenticado o None
        """
        max_attempts = getattr(settings, 'LOGIN_MAX_ATTEMPTS', 5)
        lockout_seconds = getattr(settings, 'LOGIN_LOCKOUT_SECONDS', 900)
        ip_address = UserService._get_client_ip(request)
        rate_keys = UserService._rate_limit_keys(identifier, ip_address)
        current_attempts = max(cache.get(key, 0) for key in rate_keys)

        if current_attempts >= max_attempts:
            UserService._log_login_failed(
                identifier,
                request=request,
                reason='rate_limited',
                remaining=0,
            )
            if return_detail:
                return None, 'locked', 0
            return None

        user = authenticate(username=identifier, password=password)

        if not user and '@' in identifier:
            user_lookup = User.objects.filter(email__iexact=identifier).first()
            if user_lookup:
                user = authenticate(username=user_lookup.username, password=password)

        if user and user.is_active:
            for key in rate_keys:
                cache.delete(key)

            AuditLog.objects.create(
                user=user,
                action='LOGIN',
                model_name='User',
                object_id=user.id,
                object_repr=str(user),
                changes={'action': 'user_login'},
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
            )
            if return_detail:
                return user, None, None
            return user

        new_attempts = current_attempts + 1
        for key in rate_keys:
            cache.set(key, new_attempts, timeout=lockout_seconds)

        remaining = max(max_attempts - new_attempts, 0)
        UserService._log_login_failed(
            identifier,
            request=request,
            reason='invalid_credentials',
            remaining=remaining,
        )

        if return_detail:
            return None, 'invalid', remaining
        return None

    @staticmethod
    def update_user(user, **update_data):
        """
        Actualiza los datos de un usuario.

        Args:
            user (User): Instancia del usuario
            **update_data: Datos a actualizar

        Returns:
            User: Usuario actualizado
        """
        updated_by = update_data.pop('updated_by', None)
        groups = update_data.pop('groups', None)
        user_permissions = update_data.pop('user_permissions', None)

        old_data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'department': user.department,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        old_groups = sorted(user.groups.values_list('name', flat=True))
        old_permissions = sorted(user.user_permissions.values_list('codename', flat=True))

        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        user.save()

        if groups is not None:
            user.groups.set(groups)

        if user_permissions is not None:
            user.user_permissions.set(user_permissions)

        # Registrar cambios en auditoría
        changes = {}
        for field in old_data:
            new_value = getattr(user, field)
            if old_data[field] != new_value:
                changes[field] = {'old': old_data[field], 'new': new_value}

        new_groups = sorted(user.groups.values_list('name', flat=True))
        if old_groups != new_groups:
            changes['groups'] = {'old': old_groups, 'new': new_groups}

        new_permissions = sorted(user.user_permissions.values_list('codename', flat=True))
        if old_permissions != new_permissions:
            changes['user_permissions'] = {
                'old': old_permissions,
                'new': new_permissions,
            }

        if changes:
            AuditLog.objects.create(
                user=updated_by or user,
                action='UPDATE',
                model_name='User',
                object_id=user.id,
                object_repr=str(user),
                changes=changes
            )

        return user

    @staticmethod
    def deactivate_user(user, deactivated_by):
        """
        Desactiva un usuario.

        Args:
            user (User): Usuario a desactivar
            deactivated_by (User): Usuario que realiza la acción
        """
        user.is_active = False
        user.save()

        # Registrar en auditoría
        AuditLog.objects.create(
            user=deactivated_by,
            action='UPDATE',
            model_name='User',
            object_id=user.id,
            object_repr=str(user),
            changes={'is_active': {'old': True, 'new': False}}
        )

    @staticmethod
    def get_active_users():
        """
        Obtiene todos los usuarios activos.

        Returns:
            QuerySet: Usuarios activos
        """
        return User.objects.filter(is_active=True).prefetch_related('groups', 'user_permissions')

    @staticmethod
    def get_user_by_id(user_id):
        """
        Obtiene un usuario por ID.

        Args:
            user_id (int): ID del usuario

        Returns:
            User or None: Usuario encontrado o None
        """
        try:
            return User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return None