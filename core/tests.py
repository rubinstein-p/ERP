from django.test import TestCase
from django.test import override_settings
from django.utils import timezone

from core.models import User, AuditLog, SystemParameter


class BaseModelTest(TestCase):
    """
    Tests para el modelo BaseModel.
    """

    def test_base_model_fields(self):
        """Test que BaseModel tenga los campos requeridos."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )

        # Verificar que tenga campos de auditoría
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        self.assertTrue(user.is_active)

        # Verificar que created_at sea anterior o igual a updated_at
        self.assertLessEqual(user.created_at, user.updated_at)


class UserModelTest(TestCase):
    """
    Tests para el modelo User.
    """

    def test_user_creation(self):
        """Test creación básica de usuario."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)

    def test_user_str_method(self):
        """Test método __str__ del usuario."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            first_name='John',
            last_name='Doe'
        )

        self.assertEqual(str(user), 'testuser - John Doe')

    def test_user_str_method_no_name(self):
        """Test método __str__ cuando no hay nombre."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )

        self.assertEqual(str(user), 'testuser - ')

    def test_user_additional_fields(self):
        """Test campos adicionales del modelo User."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            phone='+34123456789',
            department='IT',
            employee_id='EMP001'
        )

        self.assertEqual(user.phone, '+34123456789')
        self.assertEqual(user.department, 'IT')
        self.assertEqual(user.employee_id, 'EMP001')


class AuditLogModelTest(TestCase):
    """
    Tests para el modelo AuditLog.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )

    def test_audit_log_creation(self):
        """Test creación de log de auditoría."""
        log = AuditLog.objects.create(
            user=self.user,
            action='CREATE',
            model_name='User',
            object_id=1,
            object_repr='Test User',
            changes={'field': 'value'}
        )

        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'CREATE')
        self.assertEqual(log.model_name, 'User')
        self.assertEqual(log.object_id, 1)
        self.assertEqual(log.object_repr, 'Test User')
        self.assertEqual(log.changes, {'field': 'value'})

    def test_audit_log_str_method(self):
        """Test método __str__ del AuditLog."""
        log = AuditLog.objects.create(
            user=self.user,
            action='UPDATE',
            model_name='User',
            object_id=1,
            object_repr='Test User'
        )

        expected = f"{self.user} - UPDATE - User 1"
        self.assertEqual(str(log), expected)

    def test_audit_log_without_user(self):
        """Test log de auditoría sin usuario."""
        log = AuditLog.objects.create(
            action='SYSTEM',
            model_name='System',
            object_id=1,
            object_repr='System Event'
        )

        self.assertIsNone(log.user)
        self.assertEqual(log.action, 'SYSTEM')


class SystemParameterModelTest(TestCase):
    """
    Tests para el modelo SystemParameter.
    """

    def test_parameter_creation(self):
        """Test creación de parámetro del sistema."""
        param = SystemParameter.objects.create(
            key='TEST_PARAM',
            value='test_value',
            parameter_type='STRING',
            description='Test parameter',
            category='test'
        )

        self.assertEqual(param.key, 'TEST_PARAM')
        self.assertEqual(param.value, 'test_value')
        self.assertEqual(param.parameter_type, 'STRING')
        self.assertEqual(param.description, 'Test parameter')
        self.assertEqual(param.category, 'test')
        self.assertFalse(param.is_system)
        self.assertTrue(param.is_active)

    def test_parameter_str_method(self):
        """Test método __str__ del SystemParameter."""
        param = SystemParameter.objects.create(
            key='TEST_PARAM',
            value='test_value',
            parameter_type='STRING'
        )

        self.assertEqual(str(param), 'TEST_PARAM: test_value')

    def test_parameter_unique_key(self):
        """Test que la clave sea única."""
        SystemParameter.objects.create(
            key='UNIQUE_KEY',
            value='value1',
            parameter_type='STRING'
        )

        with self.assertRaises(Exception):  # IntegrityError
            SystemParameter.objects.create(
                key='UNIQUE_KEY',
                value='value2',
                parameter_type='STRING'
            )

    def test_parameter_ordering(self):
        """Test ordenamiento por categoría y clave."""
        param1 = SystemParameter.objects.create(
            key='B_PARAM',
            value='value',
            parameter_type='STRING',
            category='A'
        )
        param2 = SystemParameter.objects.create(
            key='A_PARAM',
            value='value',
            parameter_type='STRING',
            category='A'
        )
        param3 = SystemParameter.objects.create(
            key='C_PARAM',
            value='value',
            parameter_type='STRING',
            category='B'
        )

        params = list(SystemParameter.objects.all())
        self.assertEqual(params[0], param2)  # A_PARAM en categoría A
        self.assertEqual(params[1], param1)  # B_PARAM en categoría A
        self.assertEqual(params[2], param3)  # C_PARAM en categoría B
from django.test import TestCase
from django.core.exceptions import ValidationError

from core.models import User, SystemParameter
from core.services import UserService, ParameterService


class UserServiceTest(TestCase):
    """
    Tests para el servicio de usuarios.
    """

    def setUp(self):
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_user_success(self):
        """Test creación exitosa de usuario."""
        user = UserService.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123',
            first_name='Test',
            last_name='User'
        )

        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('newpass123'))

    def test_create_user_duplicate_username(self):
        """Test error al crear usuario con username duplicado."""
        with self.assertRaises(ValidationError):
            UserService.create_user(
                username='testuser',  # Ya existe
                email='different@example.com',
                password='pass123'
            )

    def test_create_user_duplicate_email(self):
        """Test error al crear usuario con email duplicado."""
        with self.assertRaises(ValidationError):
            UserService.create_user(
                username='differentuser',
                email='test@example.com',  # Ya existe
                password='pass123'
            )

    def test_authenticate_user_success(self):
        """Test autenticación exitosa."""
        user = UserService.authenticate_user('testuser', 'testpass123')
        self.assertEqual(user, self.test_user)

    def test_authenticate_user_wrong_password(self):
        """Test autenticación con contraseña incorrecta."""
        user = UserService.authenticate_user('testuser', 'wrongpass')
        self.assertIsNone(user)

    def test_update_user(self):
        """Test actualización de usuario."""
        updated_user = UserService.update_user(
            self.test_user,
            first_name='Updated',
            phone='+34123456789'
        )

        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.phone, '+34123456789')


class ParameterServiceTest(TestCase):
    """
    Tests para el servicio de parámetros.
    """

    def test_set_and_get_parameter_string(self):
        """Test establecer y obtener parámetro string."""
        ParameterService.set_parameter(
            key='TEST_PARAM',
            value='test_value',
            parameter_type='STRING',
            description='Test parameter'
        )

        value = ParameterService.get_parameter('TEST_PARAM')
        self.assertEqual(value, 'test_value')

    def test_set_and_get_parameter_integer(self):
        """Test establecer y obtener parámetro integer."""
        ParameterService.set_parameter(
            key='TEST_INT',
            value='42',
            parameter_type='INTEGER',
            description='Test integer'
        )

        value = ParameterService.get_parameter('TEST_INT')
        self.assertEqual(value, 42)
        self.assertIsInstance(value, int)

    def test_set_and_get_parameter_boolean(self):
        """Test establecer y obtener parámetro boolean."""
        ParameterService.set_parameter(
            key='TEST_BOOL',
            value='true',
            parameter_type='BOOLEAN',
            description='Test boolean'
        )

        value = ParameterService.get_parameter('TEST_BOOL')
        self.assertEqual(value, True)
        self.assertIsInstance(value, bool)

    def test_get_parameter_default(self):
        """Test obtener parámetro con valor por defecto."""
        value = ParameterService.get_parameter('NON_EXISTENT', default='default_value')
        self.assertEqual(value, 'default_value')

    def test_get_parameter_not_found(self):
        """Test error al obtener parámetro inexistente sin default."""
        with self.assertRaises(ValidationError):
            ParameterService.get_parameter('NON_EXISTENT')

    def test_get_parameters_by_category(self):
        """Test obtener parámetros por categoría."""
        ParameterService.set_parameter('PARAM1', 'value1', 'STRING', category='test')
        ParameterService.set_parameter('PARAM2', 'value2', 'STRING', category='test')
        ParameterService.set_parameter('PARAM3', 'value3', 'STRING', category='other')

        params = ParameterService.get_parameters_by_category('test')
        self.assertEqual(len(params), 2)
        self.assertEqual(params['PARAM1'], 'value1')
        self.assertEqual(params['PARAM2'], 'value2')

    def test_initialize_default_parameters(self):
        """Test inicialización de parámetros por defecto."""
        ParameterService.initialize_default_parameters()

        # Verificar que se crearon algunos parámetros por defecto
        company_name = ParameterService.get_parameter('COMPANY_NAME')
        self.assertEqual(company_name, 'Mi Empresa ERP')

        tax_rate = ParameterService.get_parameter('TAX_RATE')
        self.assertEqual(tax_rate, 21.0)


class UserPermissionsManagementTest(TestCase):
    """
    Tests para gestión de usuarios y permisos.
    """

    def setUp(self):
        from django.contrib.auth.models import Group, Permission

        self.Group = Group
        self.Permission = Permission
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='StaffPass123',
            is_staff=True,
        )
        self.staff_user.user_permissions.set(
            Permission.objects.filter(
                codename__in=['view_user', 'add_user', 'change_user', 'delete_user']
            )
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='RegularPass123',
        )

    def test_regular_user_cannot_access_user_management(self):
        from django.urls import reverse

        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('core:user_list'))
        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_access_user_management(self):
        from django.urls import reverse

        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('core:user_list'))
        self.assertEqual(response.status_code, 200)

    def test_create_user_with_group_and_permissions(self):
        group = self.Group.objects.create(name='Operadores')
        permission = self.Permission.objects.filter(content_type__app_label='core').first()

        user = UserService.create_user(
            username='nuevo',
            email='nuevo@example.com',
            password='PassSegura123',
            is_staff=True,
            groups=[group],
            user_permissions=[permission] if permission else [],
            created_by=self.staff_user,
        )

        self.assertTrue(user.groups.filter(name='Operadores').exists())
        if permission:
            self.assertTrue(user.user_permissions.filter(id=permission.id).exists())

    def test_update_user_permissions(self):
        group = self.Group.objects.create(name='Auditores')
        permission = self.Permission.objects.filter(content_type__app_label='core').first()

        UserService.update_user(
            self.regular_user,
            groups=[group],
            user_permissions=[permission] if permission else [],
            updated_by=self.staff_user,
        )

        self.assertTrue(self.regular_user.groups.filter(name='Auditores').exists())
        if permission:
            self.assertTrue(self.regular_user.user_permissions.filter(id=permission.id).exists())


class RoleManagementTest(TestCase):
    """
    Tests para ABM de roles.
    """

    def setUp(self):
        from django.contrib.auth.models import Group, Permission

        self.Group = Group
        self.staff_user = User.objects.create_user(
            username='staff_roles',
            email='staff_roles@example.com',
            password='StaffPass123',
            is_staff=True,
        )
        self.staff_user.user_permissions.set(
            Permission.objects.filter(
                codename__in=['view_group', 'add_group', 'change_group', 'delete_group']
            )
        )
        self.regular_user = User.objects.create_user(
            username='regular_roles',
            email='regular_roles@example.com',
            password='RegularPass123',
        )

    def test_regular_user_cannot_access_roles(self):
        from django.urls import reverse

        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('core:role_list'))
        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_create_role(self):
        from django.urls import reverse

        self.client.force_login(self.staff_user)
        response = self.client.post(
            reverse('core:role_create'),
            {'name': 'Compras', 'permissions': []},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.Group.objects.filter(name='Compras').exists())

    def test_staff_user_can_update_role(self):
        from django.urls import reverse

        role = self.Group.objects.create(name='Ventas')
        self.client.force_login(self.staff_user)
        response = self.client.post(
            reverse('core:role_update', kwargs={'pk': role.pk}),
            {'name': 'Ventas Senior', 'permissions': []},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        role.refresh_from_db()
        self.assertEqual(role.name, 'Ventas Senior')

    def test_staff_user_can_delete_role(self):
        from django.urls import reverse

        role = self.Group.objects.create(name='Temporal')
        self.client.force_login(self.staff_user)
        response = self.client.post(
            reverse('core:role_delete', kwargs={'pk': role.pk}),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.Group.objects.filter(pk=role.pk).exists())

    def test_filter_roles_by_permission(self):
        from django.contrib.auth.models import Permission
        from django.urls import reverse

        perm = Permission.objects.filter(codename__icontains='view').first()
        role_with_perm = self.Group.objects.create(name='ConPermiso')
        role_without_perm = self.Group.objects.create(name='SinPermiso')
        if perm:
            role_with_perm.permissions.add(perm)

        self.client.force_login(self.staff_user)
        query = perm.codename if perm else 'view'
        response = self.client.get(reverse('core:role_list'), {'permission_search': query})

        self.assertEqual(response.status_code, 200)
        roles = list(response.context['roles'])
        if perm:
            self.assertIn(role_with_perm, roles)
            self.assertNotIn(role_without_perm, roles)

    def test_role_list_page_size(self):
        from django.urls import reverse

        for i in range(30):
            self.Group.objects.create(name=f'Rol-{i:02d}')

        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('core:role_list'), {'page_size': '25'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['paginator'].per_page, 25)
        self.assertTrue(response.context['is_paginated'])

    def test_create_role_with_module_matrix_read_level(self):
        from core.services import RoleService
        from django.urls import reverse

        self.client.force_login(self.staff_user)
        response = self.client.post(
            reverse('core:role_create'),
            {
                'name': 'Lectores Core',
                'permissions': [],
                'permission_modules': ['core'],
                'permission_level': 'read',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        role = self.Group.objects.get(name='Lectores Core')

        expected_ids = set(
            RoleService.permissions_for_modules(['core'], access_level='read').values_list('id', flat=True)
        )
        current_ids = set(role.permissions.values_list('id', flat=True))
        self.assertTrue(expected_ids.issubset(current_ids))

    def test_permission_matrix_overview_contains_modules(self):
        from core.services import RoleService

        matrix = RoleService.get_permission_matrix_overview()
        self.assertIn('core', matrix)
        self.assertIn('masters', matrix)
        self.assertIn('levels', matrix['core'])
        self.assertIn('read', matrix['core']['levels'])

    def test_create_standard_roles_contains_required_names(self):
        from core.services import RoleService

        RoleService.create_standard_roles()
        names = set(self.Group.objects.values_list('name', flat=True))

        self.assertIn('Administrador', names)
        self.assertIn('Operador', names)
        self.assertIn('Auditor', names)
        self.assertIn('Supervisor', names)

    def test_management_command_extended_mode_creates_domain_roles(self):
        from django.core.management import call_command

        call_command('create_default_roles', '--extended')
        names = set(self.Group.objects.values_list('name', flat=True))

        self.assertIn('Administrador', names)
        self.assertIn('Operador', names)
        self.assertIn('Auditor', names)
        self.assertIn('Supervisor', names)
        self.assertIn('Operador Compras', names)
        self.assertIn('Operador Ventas', names)


class LogoutSecurityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='logout_user',
            email='logout@example.com',
            password='LogoutPass123',
        )

    def test_logout_get_not_allowed(self):
        from django.urls import reverse

        self.client.force_login(self.user)
        response = self.client.get(reverse('core:logout'))
        self.assertEqual(response.status_code, 405)

    def test_logout_post_ok(self):
        from django.urls import reverse

        self.client.force_login(self.user)
        response = self.client.post(reverse('core:logout'), follow=True)
        self.assertEqual(response.status_code, 200)


@override_settings(LOGIN_MAX_ATTEMPTS=2, LOGIN_LOCKOUT_SECONDS=60)
class LoginRateLimitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='ratelimit_user',
            email='ratelimit@example.com',
            password='StrongPass123',
        )

    def test_failed_login_creates_audit_log(self):
        from django.urls import reverse

        response = self.client.post(
            reverse('core:login'),
            {'username': self.user.username, 'password': 'wrong', 'remember_me': False},
            follow=True,
        )

        self.assertIn('X-Request-ID', response.headers)
        log = AuditLog.objects.filter(action='LOGIN_FAILED').latest('id')
        self.assertIn('request_id', log.changes)
        self.assertEqual(log.changes['request_id'], response.headers['X-Request-ID'])

    def test_login_is_blocked_after_max_attempts(self):
        from django.urls import reverse

        self.client.post(reverse('core:login'), {'username': self.user.username, 'password': 'wrong'})
        self.client.post(reverse('core:login'), {'username': self.user.username, 'password': 'wrong'})
        response = self.client.post(
            reverse('core:login'),
            {'username': self.user.username, 'password': 'wrong'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            AuditLog.objects.filter(action='LOGIN_FAILED', changes__reason='rate_limited').exists()
        )


class AccessDeniedAuditTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='noaccess_user',
            email='noaccess@example.com',
            password='NoAccess123',
        )

    def test_access_denied_is_audited(self):
        from django.urls import reverse

        self.client.force_login(self.user)
        response = self.client.get(reverse('core:user_list'))

        self.assertEqual(response.status_code, 403)
        self.assertIn('X-Request-ID', response.headers)
        log = AuditLog.objects.filter(action='ACCESS_DENIED', object_repr='/users/').latest('id')
        self.assertIn('request_id', log.changes)
        self.assertEqual(log.changes['request_id'], response.headers['X-Request-ID'])
