from django.core.cache import cache
from django.core.exceptions import ValidationError

from core.models import SystemParameter


class ParameterService:
    """
    Servicio para la gestión de parámetros del sistema.
    Maneja configuración dinámica con cache para optimización.
    """

    CACHE_KEY_PREFIX = 'system_parameter_'
    CACHE_TIMEOUT = 3600  # 1 hora

    @staticmethod
    def get_parameter(key, default=None):
        """
        Obtiene el valor de un parámetro del sistema.

        Args:
            key (str): Clave del parámetro
            default: Valor por defecto si no existe

        Returns:
            Valor del parámetro convertido al tipo apropiado
        """
        # Intentar obtener del cache primero
        cache_key = f"{ParameterService.CACHE_KEY_PREFIX}{key}"
        cached_value = cache.get(cache_key)

        if cached_value is not None:
            return cached_value

        try:
            param = SystemParameter.objects.get(key=key, is_active=True)
            value = ParameterService._convert_value(param.value, param.parameter_type)
            cache.set(cache_key, value, ParameterService.CACHE_TIMEOUT)
            return value
        except SystemParameter.DoesNotExist:
            if default is not None:
                return default
            raise ValidationError(f"Parámetro '{key}' no encontrado")

    @staticmethod
    def set_parameter(key, value, parameter_type='STRING', description='', category='', is_system=False, user=None):
        """
        Establece o actualiza un parámetro del sistema.

        Args:
            key (str): Clave del parámetro
            value: Valor del parámetro
            parameter_type (str): Tipo de parámetro
            description (str): Descripción
            category (str): Categoría
            is_system (bool): Si es parámetro del sistema
            user (User): Usuario que realiza el cambio
        """
        # Convertir valor a string para almacenamiento
        str_value = ParameterService._value_to_string(value, parameter_type)

        param, created = SystemParameter.objects.get_or_create(
            key=key,
            defaults={
                'value': str_value,
                'parameter_type': parameter_type,
                'description': description,
                'category': category,
                'is_system': is_system
            }
        )

        if not created:
            param.value = str_value
            param.parameter_type = parameter_type
            param.description = description
            param.category = category
            param.is_system = is_system
            param.save()

        # Limpiar cache
        cache_key = f"{ParameterService.CACHE_KEY_PREFIX}{key}"
        cache.delete(cache_key)

        # Registrar en auditoría si hay usuario
        if user:
            from core.services.audit_service import AuditService
            AuditService.log_action(
                user=user,
                action='UPDATE' if not created else 'CREATE',
                model_name='SystemParameter',
                object_id=param.id,
                object_repr=f"Parameter: {key}",
                changes={'value': str_value, 'type': parameter_type}
            )

    @staticmethod
    def get_parameters_by_category(category):
        """
        Obtiene todos los parámetros de una categoría.

        Args:
            category (str): Categoría de parámetros

        Returns:
            dict: Diccionario con clave: valor
        """
        params = SystemParameter.objects.filter(
            category=category,
            is_active=True
        )

        result = {}
        for param in params:
            result[param.key] = ParameterService._convert_value(
                param.value,
                param.parameter_type
            )

        return result

    @staticmethod
    def get_all_parameters():
        """
        Obtiene todos los parámetros activos.

        Returns:
            dict: Diccionario con clave: valor
        """
        params = SystemParameter.objects.filter(is_active=True)

        result = {}
        for param in params:
            result[param.key] = ParameterService._convert_value(
                param.value,
                param.parameter_type
            )

        return result

    @staticmethod
    def delete_parameter(key, user=None):
        """
        Elimina (desactiva) un parámetro.

        Args:
            key (str): Clave del parámetro
            user (User): Usuario que realiza la eliminación
        """
        try:
            param = SystemParameter.objects.get(key=key, is_active=True)
            param.is_active = False
            param.save()

            # Limpiar cache
            cache_key = f"{ParameterService.CACHE_KEY_PREFIX}{key}"
            cache.delete(cache_key)

            # Registrar en auditoría
            if user:
                from core.services.audit_service import AuditService
                AuditService.log_action(
                    user=user,
                    action='DELETE',
                    model_name='SystemParameter',
                    object_id=param.id,
                    object_repr=f"Parameter: {key}",
                    changes={'is_active': False}
                )

        except SystemParameter.DoesNotExist:
            raise ValidationError(f"Parámetro '{key}' no encontrado")

    @staticmethod
    def initialize_default_parameters():
        """
        Inicializa parámetros por defecto del sistema.
        """
        default_params = [
            {
                'key': 'COMPANY_NAME',
                'value': 'Mi Empresa ERP',
                'parameter_type': 'STRING',
                'description': 'Nombre de la empresa',
                'category': 'general'
            },
            {
                'key': 'DEFAULT_CURRENCY',
                'value': 'EUR',
                'parameter_type': 'STRING',
                'description': 'Moneda por defecto',
                'category': 'finance'
            },
            {
                'key': 'TAX_RATE',
                'value': '21.0',
                'parameter_type': 'DECIMAL',
                'description': 'Tasa de IVA por defecto (%)',
                'category': 'finance'
            },
            {
                'key': 'SESSION_TIMEOUT',
                'value': '3600',
                'parameter_type': 'INTEGER',
                'description': 'Tiempo de expiración de sesión (segundos)',
                'category': 'security'
            },
            {
                'key': 'MAX_LOGIN_ATTEMPTS',
                'value': '5',
                'parameter_type': 'INTEGER',
                'description': 'Máximo número de intentos de login',
                'category': 'security'
            },
            {
                'key': 'ENABLE_AUDIT_LOG',
                'value': 'true',
                'parameter_type': 'BOOLEAN',
                'description': 'Habilitar registro de auditoría',
                'category': 'system'
            }
        ]

        for param_data in default_params:
            SystemParameter.objects.get_or_create(
                key=param_data['key'],
                defaults=param_data
            )

    @staticmethod
    def _convert_value(value_str, parameter_type):
        """
        Convierte un valor string al tipo apropiado.

        Args:
            value_str (str): Valor como string
            parameter_type (str): Tipo de parámetro

        Returns:
            Valor convertido al tipo apropiado
        """
        if parameter_type == 'INTEGER':
            return int(value_str)
        elif parameter_type == 'DECIMAL':
            return float(value_str)
        elif parameter_type == 'BOOLEAN':
            return value_str.lower() in ('true', '1', 'yes', 'on')
        elif parameter_type == 'JSON':
            import json
            return json.loads(value_str)
        else:  # STRING
            return value_str

    @staticmethod
    def _value_to_string(value, parameter_type):
        """
        Convierte un valor al formato string para almacenamiento.

        Args:
            value: Valor a convertir
            parameter_type (str): Tipo de parámetro

        Returns:
            str: Valor como string
        """
        if parameter_type == 'DATE':
            return value.isoformat()
        elif parameter_type == 'JSON':
            import json
            return json.dumps(value)
        elif parameter_type == 'BOOLEAN':
            return 'true' if value else 'false'
        else:
            return str(value)