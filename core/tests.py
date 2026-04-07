from django.test import TestCase
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
