from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from core.models import AuditLog


class AuditService:
    """
    Servicio para la gestión de auditoría del sistema.
    Maneja logs de actividades y reportes de auditoría.
    """

    @staticmethod
    def log_action(user, action, model_name, object_id, object_repr, changes=None, ip_address=None, user_agent=None):
        """
        Registra una acción en el log de auditoría.

        Args:
            user (User): Usuario que realiza la acción
            action (str): Tipo de acción (CREATE, UPDATE, DELETE, etc.)
            model_name (str): Nombre del modelo
            object_id (int): ID del objeto
            object_repr (str): Representación del objeto
            changes (dict, optional): Cambios realizados
            ip_address (str, optional): Dirección IP
            user_agent (str, optional): User Agent
        """
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def get_user_activity(user, days=30):
        """
        Obtiene la actividad de un usuario en los últimos N días.

        Args:
            user (User): Usuario
            days (int): Número de días hacia atrás

        Returns:
            QuerySet: Logs de auditoría del usuario
        """
        since_date = timezone.now() - timedelta(days=days)
        return AuditLog.objects.filter(
            user=user,
            timestamp__gte=since_date
        ).order_by('-timestamp')

    @staticmethod
    def get_model_activity(model_name, days=30):
        """
        Obtiene la actividad de un modelo específico.

        Args:
            model_name (str): Nombre del modelo
            days (int): Número de días hacia atrás

        Returns:
            QuerySet: Logs de auditoría del modelo
        """
        since_date = timezone.now() - timedelta(days=days)
        return AuditLog.objects.filter(
            model_name=model_name,
            timestamp__gte=since_date
        ).order_by('-timestamp')

    @staticmethod
    def get_recent_activity(limit=50):
        """
        Obtiene la actividad reciente del sistema.

        Args:
            limit (int): Número máximo de registros

        Returns:
            QuerySet: Logs de auditoría recientes
        """
        return AuditLog.objects.all().order_by('-timestamp')[:limit]

    @staticmethod
    def search_activity(search_term=None, action=None, user=None, model_name=None, start_date=None, end_date=None):
        """
        Busca actividad en los logs de auditoría con filtros.

        Args:
            search_term (str, optional): Término de búsqueda
            action (str, optional): Tipo de acción
            user (User, optional): Usuario específico
            model_name (str, optional): Nombre del modelo
            start_date (datetime, optional): Fecha de inicio
            end_date (datetime, optional): Fecha de fin

        Returns:
            QuerySet: Logs filtrados
        """
        queryset = AuditLog.objects.all()

        if search_term:
            queryset = queryset.filter(
                Q(object_repr__icontains=search_term) |
                Q(changes__icontains=search_term)
            )

        if action:
            queryset = queryset.filter(action=action)

        if user:
            queryset = queryset.filter(user=user)

        if model_name:
            queryset = queryset.filter(model_name=model_name)

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)

        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset.order_by('-timestamp')

    @staticmethod
    def get_activity_summary(days=30):
        """
        Obtiene un resumen de actividad del sistema.

        Args:
            days (int): Número de días para el resumen

        Returns:
            dict: Resumen de actividad
        """
        since_date = timezone.now() - timedelta(days=days)

        logs = AuditLog.objects.filter(timestamp__gte=since_date)

        summary = {
            'total_actions': logs.count(),
            'actions_by_type': {},
            'actions_by_user': {},
            'actions_by_model': {},
            'period_days': days
        }

        # Acciones por tipo
        for log in logs:
            summary['actions_by_type'][log.action] = summary['actions_by_type'].get(log.action, 0) + 1

            if log.user:
                user_key = str(log.user)
                summary['actions_by_user'][user_key] = summary['actions_by_user'].get(user_key, 0) + 1

            summary['actions_by_model'][log.model_name] = summary['actions_by_model'].get(log.model_name, 0) + 1

        return summary

    @staticmethod
    def cleanup_old_logs(days_to_keep=365):
        """
        Elimina logs de auditoría antiguos.

        Args:
            days_to_keep (int): Días de logs a mantener

        Returns:
            int: Número de logs eliminados
        """
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        old_logs = AuditLog.objects.filter(timestamp__lt=cutoff_date)
        count = old_logs.count()
        old_logs.delete()
        return count