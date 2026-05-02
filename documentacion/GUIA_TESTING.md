# Guía de Testing: Tests Unitarios e Integración en el ERP

Fecha: 2026-05-02

## Introducción

Esta guía cubre cómo escribir, ejecutar y mantener tests en el ERP Django. El proyecto utiliza **Django's TestCase** (framework unittest) junto con **pytest** para máxima flexibilidad.

Todos los tests deben ejecutarse en verde ✅ antes de hacer commit o deploy.

---

## Frameworks y Herramientas

| Herramienta | Versión | Propósito |
|------------|---------|----------|
| `unittest` | Incluido en Django | Framework base para tests |
| `pytest` | 8.3.3 | Ejecución alternativa, mejor reportes |
| `pytest-django` | 4.8.0 | Integración con Django |
| `coverage` | 7.6.1 | Medición de cobertura de código |

### ¿Por qué unittest y no pytest?

El proyecto usa **unittest** (Django TestCase) en `core/tests.py` porque:
- ✅ Integrado directamente en Django
- ✅ Transacciones automáticas (rollback después de cada test)
- ✅ Fixtures con `setUp()` y `tearDown()`
- ✅ No requiere instalación adicional

Pero también puedes usar **pytest** para:
- Sintaxis más limpia
- Mejor reportes
- Fixtures reutilizables

---

## Estructura de Tests en el Proyecto

### Ubicación: `app/tests/`

```
app/
├── tests/
│   ├── __init__.py
│   ├── test_models.py      ← Tests de modelos
│   ├── test_services.py    ← Tests de servicios
│   ├── test_views.py       ← Tests de vistas
│   ├── test_forms.py       ← Tests de formularios
│   └── conftest.py         ← Fixtures comunes (pytest)
```

### Ubicación alternativa: `app/tests.py`

Solo para apps pequeñas sin muchos tests:

```
app/
├── tests.py                ← Todos los tests en un archivo
```

**Importante:** No mezclar `tests.py` con paquete `tests/` en la misma app.

---

## Patrones de Tests en Core

El archivo [core/tests.py](core/tests.py) contiene 12 clases de test como referencia:

### 1. BaseModelTest

```python
class BaseModelTest(TestCase):
    """Tests para el modelo base con campos de auditoría."""
    
    def test_base_model_fields(self):
        """Verifica que BaseModel tenga campos de auditoría."""
        user = User.objects.create_user(
            username='test',
            email='test@test.com',
            password='testpass123'
        )
        
        # BaseModel fields
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        self.assertTrue(user.is_active)
```

### 2. UserModelTest

```python
class UserModelTest(TestCase):
    """Tests para el modelo User."""
    
    def test_create_user(self):
        """Test crear un usuario."""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_string_representation(self):
        """Test que __str__ retorna nombre completo o username."""
        user = User.objects.create_user(
            username='testuser',
            first_name='John',
            last_name='Doe'
        )
        
        # Si tiene nombre y apellido, retorna "John Doe"
        self.assertIn('John', str(user))
```

### 3. UserServiceTest

```python
class UserServiceTest(TestCase):
    """Tests para el servicio de usuarios."""
    
    def setUp(self):
        self.user_service = UserService
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_authenticate_user_success(self):
        """Test autenticación exitosa."""
        authenticated_user = self.user_service.authenticate_user(
            username='testuser',
            password='testpass123'
        )
        
        self.assertEqual(authenticated_user.username, 'testuser')
    
    def test_authenticate_user_failure(self):
        """Test autenticación fallida."""
        authenticated_user = self.user_service.authenticate_user(
            username='testuser',
            password='wrongpassword'
        )
        
        self.assertIsNone(authenticated_user)
```

---

## Cómo Escribir Tests

### Paso 1: Crear la clase de test

```python
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class SaleServiceTest(TestCase):
    """Tests para el servicio de ventas."""
```

### Paso 2: Setup de fixtures

```python
class SaleServiceTest(TestCase):
    
    def setUp(self):
        """Se ejecuta antes de cada test."""
        self.user = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123',
            is_staff=True
        )
        
        self.sale = Sale.objects.create(
            sale_number='SALE-001',
            customer_name='Cliente Test',
            seller=self.user
        )
    
    def tearDown(self):
        """Se ejecuta después de cada test (limpieza)."""
        # Django hace rollback automático, aquí solo código customizado si aplica
        pass
```

### Paso 3: Escribir un test

```python
def test_create_sale_success(self):
    """Descripción clara del comportamiento esperado."""
    # Arrange (preparar datos)
    items_data = [
        {'product_name': 'Producto 1', 'quantity': 5, 'unit_price': 100},
    ]
    
    # Act (ejecutar la acción)
    sale = SaleService.create_sale(
        customer_name='New Cliente',
        customer_email='new@test.com',
        seller=self.user,
        items_data=items_data
    )
    
    # Assert (verificar resultados)
    self.assertIsNotNone(sale.id)
    self.assertEqual(sale.customer_name, 'New Cliente')
    self.assertEqual(sale.items.count(), 1)
```

### Paso 4: Assertions comunes

```python
# Igualdad
self.assertEqual(actual, expected)
self.assertNotEqual(actual, expected)

# Valores booleanos
self.assertTrue(condition)
self.assertFalse(condition)

# Nulidad
self.assertIsNone(value)
self.assertIsNotNone(value)

# Existencia en colecciones
self.assertIn(element, collection)
self.assertNotIn(element, collection)

# Excepciones
with self.assertRaises(ValidationError):
    problematic_function()

# Cantidad de elementos
self.assertEqual(queryset.count(), 2)

# Orden
self.assertEqual(list(queryset), [obj1, obj2])
```

---

## Tests por Tipo de Componente

### Tests de Modelos

```python
from django.test import TestCase
from sales.models import Sale, SaleItem

class SaleModelTest(TestCase):
    """Tests para el modelo Sale."""
    
    def setUp(self):
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_create_sale(self):
        """Test crear una venta."""
        sale = Sale.objects.create(
            sale_number='SALE-001',
            customer_name='Cliente Test',
            seller=self.seller,
        )
        
        self.assertIsNotNone(sale.id)
        self.assertEqual(sale.sale_status, 'draft')
    
    def test_sale_validation_error(self):
        """Test que validaciones se ejecutan."""
        from datetime import timedelta
        from django.utils import timezone
        from django.core.exceptions import ValidationError
        
        sale = Sale(
            sale_number='SALE-001',
            customer_name='Cliente',
            seller=self.seller,
            sale_date=timezone.now().date(),
            delivery_date=timezone.now().date() - timedelta(days=1)  # Anterior a sale_date
        )
        
        with self.assertRaises(ValidationError):
            sale.full_clean()
```

### Tests de Servicios

```python
from django.test import TestCase
from sales.services import SaleService
from django.core.exceptions import ValidationError

class SaleServiceTest(TestCase):
    """Tests para el servicio SaleService."""
    
    def test_create_sale_with_items(self):
        """Test crear venta con ítems."""
        seller = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123',
            is_staff=True
        )
        
        sale = SaleService.create_sale(
            customer_name='Cliente Test',
            customer_email='cliente@test.com',
            seller=seller,
            items_data=[
                {'product_name': 'Producto 1', 'quantity': 5, 'unit_price': 100},
                {'product_name': 'Producto 2', 'quantity': 3, 'unit_price': 50},
            ]
        )
        
        self.assertEqual(sale.items.count(), 2)
        self.assertEqual(sale.subtotal, 650)  # 5*100 + 3*50
    
    def test_create_sale_non_staff_fails(self):
        """Test que no-staff no puede crear ventas."""
        non_staff = User.objects.create_user(
            username='customer',
            email='customer@test.com',
            password='testpass123',
            is_staff=False
        )
        
        with self.assertRaises(ValidationError) as cm:
            SaleService.create_sale(
                customer_name='Cliente Test',
                customer_email='cliente@test.com',
                seller=non_staff,
            )
        
        self.assertIn('staff', str(cm.exception).lower())
```

### Tests de Formularios

```python
from django.test import TestCase
from sales.forms import SaleForm

class SaleFormTest(TestCase):
    """Tests para el formulario SaleForm."""
    
    def test_form_valid_data(self):
        """Test formulario con datos válidos."""
        form_data = {
            'customer_name': 'Cliente Test',
            'customer_email': 'cliente@test.com',
            'customer_phone': '+54 9 123 456789',
            'delivery_date': '2026-05-15',
            'notes': 'Test notes'
        }
        form = SaleForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_missing_required_field(self):
        """Test formulario sin campo requerido."""
        form_data = {
            'customer_email': 'cliente@test.com',
            # Falta customer_name
        }
        form = SaleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('customer_name', form.errors)
```

### Tests de Vistas

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class SaleListViewTest(TestCase):
    """Tests para la vista SaleListView."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            is_staff=True
        )
        self.sale = Sale.objects.create(
            sale_number='SALE-001',
            customer_name='Cliente Test',
            seller=self.user,
        )
    
    def test_list_view_requires_login(self):
        """Test que lista requiere login."""
        response = self.client.get(reverse('sales:sale_list'))
        self.assertEqual(response.status_code, 302)  # Redirect a login
    
    def test_list_view_success(self):
        """Test que lista muestra ventas."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('sales:sale_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.sale, response.context['sales'])
    
    def test_create_view_post_success(self):
        """Test crear venta por POST."""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'customer_name': 'Nueva Cliente',
            'customer_email': 'nueva@test.com',
            'customer_phone': '+54 9 123 456789',
        }
        response = self.client.post(reverse('sales:sale_create'), data=form_data)
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(Sale.objects.count(), 2)
```

---

## Ejecutar Tests

### Ejecutar todos los tests

```bash
python manage.py test
```

### Ejecutar tests de una app específica

```bash
python manage.py test sales
```

### Ejecutar una clase de test

```bash
python manage.py test sales.tests.SaleServiceTest
```

### Ejecutar un método de test específico

```bash
python manage.py test sales.tests.SaleServiceTest.test_create_sale_success
```

### Ejecutar con verbosidad

```bash
python manage.py test sales --verbosity=2
```

### Ejecutar con pytest (alternativa)

```bash
pytest sales/
pytest sales/tests/test_models.py
pytest sales/tests/test_models.py::SaleModelTest::test_create_sale
```

---

## Cobertura de Código

Mide qué porcentaje de código está cubierto por tests:

```bash
# Ejecutar coverage
coverage run --source='.' manage.py test

# Ver reporte en consola
coverage report

# Ver reporte HTML
coverage html
# Luego abre htmlcov/index.html en el navegador
```

### Resultado esperado

```
Name                    Stmts   Miss  Cover
--------------------------------------------
sales/models.py             40      5    87%
sales/services.py           60      8    87%
sales/forms.py              25      2    92%
sales/views.py              80     15    81%
sales/tests/__init__.py      0      0   100%
--------------------------------------------
TOTAL                      205     30    85%
```

**Objetivo:** Mínimo 80% de cobertura por app nueva.

---

## Fixtures Reutilizables

### Con unittest

```python
class CommonFixtures(TestCase):
    """Base class con fixtures comunes."""
    
    @classmethod
    def setUpClass(cls):
        """Se ejecuta una sola vez antes de todos los tests de la clase."""
        super().setUpClass()
        cls.seller_user = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123',
            is_staff=True
        )
    
    def setUp(self):
        """Se ejecuta antes de cada test."""
        self.sale = Sale.objects.create(
            sale_number='SALE-001',
            customer_name='Cliente Test',
            seller=self.seller_user,
        )

class SaleServiceTest(CommonFixtures):
    """Hereda fixtures comunes."""
    pass
```

### Con pytest (conftest.py)

```python
# sales/tests/conftest.py
import pytest
from django.contrib.auth import get_user_model
from sales.models import Sale

User = get_user_model()

@pytest.fixture
def seller_user(db):
    """Fixture que crea un usuario vendedor."""
    return User.objects.create_user(
        username='seller',
        email='seller@test.com',
        password='testpass123',
        is_staff=True
    )

@pytest.fixture
def sale(db, seller_user):
    """Fixture que crea una venta."""
    return Sale.objects.create(
        sale_number='SALE-001',
        customer_name='Cliente Test',
        seller=seller_user,
    )

# sales/tests/test_models.py (con pytest)
def test_create_sale(sale):
    """Test usando fixture."""
    assert sale.id is not None
    assert sale.customer_name == 'Cliente Test'
```

---

## Mocking y Patching

Para tests que requieren dependencias externas:

```python
from unittest.mock import patch, Mock
from django.test import TestCase
from sales.services import SaleService

class SaleServiceWithMockTest(TestCase):
    """Tests con mocks para dependencias externas."""
    
    @patch('sales.services.audit_service.log_action')
    def test_create_sale_logs_audit(self, mock_log_action):
        """Test que se registra auditoría."""
        seller = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123',
            is_staff=True
        )
        
        SaleService.create_sale(
            customer_name='Cliente',
            customer_email='cliente@test.com',
            seller=seller,
        )
        
        # Verifica que log_action fue llamado
        self.assertTrue(mock_log_action.called)
        mock_log_action.assert_called()
```

---

## Tests de Integración

Tests que verifican flujos completos:

```python
from django.test import TestCase, Client
from django.urls import reverse

class SaleEndToEndTest(TestCase):
    """Test flujo completo: crear venta desde login hasta confirmación."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_complete_sale_workflow(self):
        """Test flujo: login → crear venta → ver detalle → editar → delete."""
        # 1. Login
        logged_in = self.client.login(username='seller', password='testpass123')
        self.assertTrue(logged_in)
        
        # 2. Acceder a crear venta
        response = self.client.get(reverse('sales:sale_create'))
        self.assertEqual(response.status_code, 200)
        
        # 3. Crear venta
        form_data = {
            'customer_name': 'Cliente Test',
            'customer_email': 'cliente@test.com',
        }
        response = self.client.post(reverse('sales:sale_create'), data=form_data)
        self.assertEqual(response.status_code, 302)
        
        # 4. Verificar que venta existe
        sale = Sale.objects.first()
        self.assertIsNotNone(sale)
        
        # 5. Ver detalle
        response = self.client.get(reverse('sales:sale_detail', args=[sale.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(sale.customer_name, response.content.decode())
```

---

## Checklist para Tests

Antes de considerar un módulo listo:

- [ ] Tests de modelos: validaciones, campos, relaciones
- [ ] Tests de servicios: lógica de negocio, excepciones
- [ ] Tests de formularios: validaciones, campos requeridos
- [ ] Tests de vistas: permiso, autenticación, respuestas HTTP
- [ ] Tests de integración: flujos completos
- [ ] Cobertura de código: mínimo 80%
- [ ] Todos los tests en verde: `python manage.py test`
- [ ] No hay warnings: `--verbosity=2`
- [ ] Fixtures reutilizables y limpias

---

## Troubleshooting

### Error: "django.db.utils.ProgrammingError: relation does not exist"

**Causa:** Las migraciones no se ejecutaron en la BD de test.

**Solución:**

```bash
python manage.py migrate
```

### Error: "TransactionManagementError"

**Causa:** Fuera de transacción o BD no configurada.

**Solución:** Asegúrate de heredar de `TestCase`, no `SimpleTestCase`:

```python
from django.test import TestCase  # ✅ Correcto

class MyTest(TestCase):
    pass
```

### Test pasa en local pero falla en CI/CD

**Causa:** Dependencias no están aisladas, tests no son determinísticos.

**Solución:**

- Usa fixtures en `setUp()`
- No dependas de orden de ejecución
- Usa `@override_settings` para cambiar configuración

```python
from django.test import override_settings

class MyTest(TestCase):
    @override_settings(DEBUG=False)
    def test_production_behavior(self):
        pass
```

---

## Recursos Útiles

- [Django Testing Documentation](https://docs.djangoproject.com/en/6.0/topics/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-django Plugin](https://pytest-django.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

## Próximos Pasos

1. Escribir tests antes de código (TDD)
2. Usar Continuous Integration (GitHub Actions)
3. Agregar tests de performance
4. Agregar tests de seguridad (SQL injection, XSS)
5. Usar factories para fixtures más complejas (factory_boy)
