from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin

from core.models import AuditLog


def _get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class AccessAuditMixin:
    """
    Registra intentos de acceso denegado en auditoria.
    """

    def _audit_access_denied(self, reason='access_denied'):
        request = self.request
        user = request.user if request.user.is_authenticated else None
        object_id = getattr(getattr(self, 'object', None), 'id', 0) or 0
        AuditLog.objects.create(
            user=user,
            action='ACCESS_DENIED',
            model_name=self.__class__.__name__,
            object_id=object_id,
            object_repr=request.path,
            changes={
                'reason': reason,
                'method': request.method,
            },
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )


class StaffRequiredMixin(AccessAuditMixin, UserPassesTestMixin):
    """
    Restringe acceso a usuarios de staff o superusuarios.
    """
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_staff or user.is_superuser)

    def handle_no_permission(self):
        self._audit_access_denied(reason='staff_required')
        return super().handle_no_permission()


class PermissionAuditRequiredMixin(AccessAuditMixin, PermissionRequiredMixin):
    """
    Variante de PermissionRequiredMixin que audita denegaciones.
    """

    def handle_no_permission(self):
        required = self.get_permission_required()
        reason = f"missing_permission:{','.join(required)}" if required else 'missing_permission'
        self._audit_access_denied(reason=reason)
        return super().handle_no_permission()
