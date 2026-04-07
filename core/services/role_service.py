from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.db.models import Q

from core.models import AuditLog


class RoleService:
    """
    Servicio para gestion de roles (grupos) y sus permisos.
    """

    MODULE_LABELS = {
        'core': 'Core (Seguridad)',
        'masters': 'Maestros',
        'purchases': 'Compras',
        'sales': 'Ventas',
        'inventory': 'Inventario',
        'accounting': 'Contabilidad',
        'reports': 'Reportes',
    }

    ACCESS_LEVEL_ACTIONS = {
        'read': ['view'],
        'operate': ['view', 'add', 'change'],
        'manage': ['view', 'add', 'change', 'delete'],
    }

    ACCESS_LEVEL_CHOICES = [
        ('read', 'Solo lectura'),
        ('operate', 'Operacion (crear/editar)'),
        ('manage', 'Administracion completa'),
    ]

    @staticmethod
    def get_roles():
        return Group.objects.prefetch_related('permissions', 'user_set').order_by('name')

    @staticmethod
    def create_role(name, permissions=None, created_by=None):
        role_name = (name or '').strip()
        if Group.objects.filter(name__iexact=role_name).exists():
            raise ValidationError('Ya existe un rol con ese nombre')

        role = Group.objects.create(name=role_name)
        if permissions is not None:
            role.permissions.set(permissions)

        AuditLog.objects.create(
            user=created_by,
            action='CREATE',
            model_name='Group',
            object_id=role.id,
            object_repr=role.name,
            changes={
                'action': 'role_created',
                'permissions_count': role.permissions.count(),
            },
        )
        return role

    @staticmethod
    def update_role(role, name=None, permissions=None, updated_by=None):
        old_name = role.name
        old_permissions = sorted(role.permissions.values_list('codename', flat=True))

        if name is not None:
            role_name = name.strip()
            qs = Group.objects.filter(name__iexact=role_name).exclude(pk=role.pk)
            if qs.exists():
                raise ValidationError('Ya existe un rol con ese nombre')
            role.name = role_name
            role.save()

        if permissions is not None:
            role.permissions.set(permissions)

        changes = {}
        if old_name != role.name:
            changes['name'] = {'old': old_name, 'new': role.name}

        new_permissions = sorted(role.permissions.values_list('codename', flat=True))
        if old_permissions != new_permissions:
            changes['permissions'] = {
                'old': old_permissions,
                'new': new_permissions,
            }

        if changes:
            AuditLog.objects.create(
                user=updated_by,
                action='UPDATE',
                model_name='Group',
                object_id=role.id,
                object_repr=role.name,
                changes=changes,
            )

        return role

    @staticmethod
    def delete_role(role, deleted_by=None):
        role_id = role.id
        role_name = role.name
        users_count = role.user_set.count()
        role.delete()

        AuditLog.objects.create(
            user=deleted_by,
            action='DELETE',
            model_name='Group',
            object_id=role_id,
            object_repr=role_name,
            changes={'assigned_users': users_count},
        )

    @staticmethod
    def _permissions_for_apps(app_labels, actions=None):
        queryset = Permission.objects.filter(content_type__app_label__in=app_labels)
        if actions:
            query = Q()
            for action in actions:
                query |= Q(codename__startswith=f'{action}_')
            queryset = queryset.filter(query)
        return queryset.distinct()

    @staticmethod
    def get_module_choices():
        return [(key, label) for key, label in RoleService.MODULE_LABELS.items()]

    @staticmethod
    def permissions_for_modules(app_labels, access_level='operate'):
        actions = RoleService.ACCESS_LEVEL_ACTIONS.get(access_level, RoleService.ACCESS_LEVEL_ACTIONS['operate'])
        return RoleService._permissions_for_apps(app_labels, actions=actions)

    @staticmethod
    def get_permission_matrix_overview():
        """
        Devuelve la matriz de permisos por modulo y nivel.
        """
        matrix = {}
        for module_key, module_label in RoleService.MODULE_LABELS.items():
            matrix[module_key] = {
                'label': module_label,
                'levels': {},
            }
            for level_key, _level_label in RoleService.ACCESS_LEVEL_CHOICES:
                perms = RoleService.permissions_for_modules([module_key], access_level=level_key)
                matrix[module_key]['levels'][level_key] = perms
        return matrix

    @staticmethod
    def get_standard_role_matrix():
        """
        Matriz estandar de roles base del ERP.
        """
        business_modules = ['masters', 'purchases', 'sales', 'inventory', 'accounting', 'reports']
        core_read = RoleService.permissions_for_modules(['core'], access_level='read')
        business_operate = RoleService.permissions_for_modules(business_modules, access_level='operate')
        business_manage = RoleService.permissions_for_modules(business_modules, access_level='manage')

        operator_ids = set(core_read.values_list('id', flat=True)).union(
            set(business_operate.values_list('id', flat=True))
        )
        supervisor_ids = set(core_read.values_list('id', flat=True)).union(
            set(business_manage.values_list('id', flat=True))
        )

        return {
            'Administrador': Permission.objects.all(),
            'Operador': Permission.objects.filter(id__in=operator_ids),
            'Auditor': RoleService.permissions_for_modules(['core'] + business_modules, access_level='read'),
            'Supervisor': Permission.objects.filter(id__in=supervisor_ids),
        }

    @staticmethod
    def get_extended_role_matrix():
        """
        Matriz extendida por dominio para operaciones especificas.
        """
        return {
            'Administrador de Seguridad': RoleService._permissions_for_apps(
                ['core', 'auth'],
                actions=['view', 'add', 'change', 'delete'],
            ),
            'Operador Maestros': RoleService.permissions_for_modules(['masters'], access_level='operate'),
            'Operador Compras': RoleService.permissions_for_modules(['purchases'], access_level='operate'),
            'Operador Ventas': RoleService.permissions_for_modules(['sales'], access_level='operate'),
            'Operador Inventario': RoleService.permissions_for_modules(['inventory'], access_level='operate'),
            'Operador Contabilidad': RoleService.permissions_for_modules(['accounting'], access_level='operate'),
            'Analista Reportes': RoleService.permissions_for_modules(['reports'], access_level='read'),
        }

    @staticmethod
    def _sync_role_matrix(role_matrix, updated_by=None):
        created = 0
        updated = 0

        for role_name, permissions in role_matrix.items():
            role, was_created = Group.objects.get_or_create(name=role_name)
            old_permissions = set(role.permissions.values_list('id', flat=True))
            new_permissions = set(permissions.values_list('id', flat=True))

            if old_permissions != new_permissions:
                role.permissions.set(permissions)
                if was_created:
                    created += 1
                else:
                    updated += 1

                AuditLog.objects.create(
                    user=updated_by,
                    action='CREATE' if was_created else 'UPDATE',
                    model_name='Group',
                    object_id=role.id,
                    object_repr=role.name,
                    changes={'permissions_count': len(new_permissions)},
                )
            elif was_created:
                created += 1

        return {
            'created': created,
            'updated': updated,
            'total_roles': len(role_matrix),
        }

    @staticmethod
    def create_standard_roles(updated_by=None):
        """
        Crea o actualiza solo roles estandar.

        Roles: Administrador, Operador, Auditor, Supervisor.
        """
        role_matrix = RoleService.get_standard_role_matrix()
        return RoleService._sync_role_matrix(role_matrix, updated_by=updated_by)

    @staticmethod
    def create_default_roles(updated_by=None, include_extended=True):
        """
        Crea o actualiza roles del sistema.

        Returns:
            dict: resumen con altas, actualizaciones y conteo de roles
        """
        role_matrix = RoleService.get_standard_role_matrix()
        if include_extended:
            role_matrix.update(RoleService.get_extended_role_matrix())
        return RoleService._sync_role_matrix(role_matrix, updated_by=updated_by)
