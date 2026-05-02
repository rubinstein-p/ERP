# FAQ y Troubleshooting: Preguntas Frecuentes y Soluciones

Fecha: 2026-05-02

## Tabla de Contenidos

1. [Preguntas Frecuentes de Desarrollo](#preguntas-frecuentes-de-desarrollo)
2. [Testing y Debugging](#testing-y-debugging)
3. [Deployment y Producción](#deployment-y-producción)
4. [Seguridad y Permisos](#seguridad-y-permisos)
5. [Performance y Cache](#performance-y-cache)
6. [Errores Comunes](#errores-comunes)

---

## Preguntas Frecuentes de Desarrollo

### P1: ¿Cómo agrego un nuevo campo a un modelo existente?

**Respuesta:**

1. Añade el campo en `models/mi_modelo.py`:

```python
class Sale(BaseModel):
    # ... campos existentes ...
    new_field = models.CharField(max_length=100)  # Nuevo campo
```

2. Crea una migración:

```bash
python manage.py makemigrations sales
```

3. Revisa la migración generada:

```bash
cat sales/migrations/0002_sale_new_field.py
```

4. Aplica la migración:

```bash
python manage.py migrate sales
```

5. Si es en producción, asegúrate de hacer backup antes:

```bash
pg_dump erp_production > backup_before_migration.sql
python manage.py migrate sales
```

---

### P2: ¿Cómo agrego un nuevo permiso personalizado?

**Respuesta:**

En Django, los permisos se crean automáticamente para cada modelo (add_model, change_model, delete_model, view_model).

Para crear permisos **personalizados**, en `models/mi_modelo.py`:

```python
class Sale(BaseModel):
    class Meta:
        permissions = [
            ("can_export_sales", "Can export sales to PDF"),
            ("can_approve_sale", "Can approve pending sales"),
        ]
```

Luego crea una migración:

```bash
python manage.py makemigrations
python manage.py migrate
```

Para asignar a un rol:

```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Obtener permiso
content_type = ContentType.objects.get(app_label='sales', model='sale')
permission = Permission.objects.get(codename='can_export_sales')

# Asignar a grupo
group = Group.objects.get(name='Operador')
group.permissions.add(permission)
```

---

### P3: ¿Cómo cambio la zona horaria del ERP?

**Respuesta:**

Edita `.env`:

```bash
TIME_ZONE=America/Argentina/Buenos_Aires  # o tu zona horaria
```

Opciones comunes para Argentina:

```
America/Argentina/Buenos_Aires
America/Argentina/Cordoba
America/Argentina/Tucuman
America/Argentina/Mendoza
America/Argentina/Rio_Gallegos
```

Reinicia Django:

```bash
python manage.py runserver
# o
sudo systemctl restart erp-gunicorn
```

Verifica en Django shell:

```bash
python manage.py shell
>>> from django.utils import timezone
>>> timezone.now()
```

---

### P4: ¿Cómo configuro email en desarrollo?

**Respuesta:**

En `.env`:

```bash
# Opción 1: Console (prints a stdout)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Opción 2: LocMem (guarda en memoria para testing)
EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend

# Opción 3: SMTP real (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=ERP <noreply@gmail.com>
```

Para Gmail, necesitas **App Password** (no tu contraseña):

1. Habilita 2-Factor Authentication en tu cuenta Google
2. Ve a [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Genera una App Password para "Mail" y "Windows"
4. Usa esa contraseña en EMAIL_HOST_PASSWORD

---

### P5: ¿Cómo reseteo la base de datos de desarrollo?

**Respuesta:**

```bash
# Eliminar todas las migraciones aplicadas
python manage.py migrate --zero

# O borrar la BD si es SQLite
rm db.sqlite3

# Recrear desde cero
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Inicializar roles
python manage.py create_default_roles --extended
```

**Advertencia:** Esto elimina **todos los datos**. Usa solo en desarrollo.

---

### P6: ¿Cómo creo usuarios de prueba rápidamente?

**Respuesta:**

Crea un script `create_test_users.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

# Datos de usuarios
users_data = [
    {'username': 'admin', 'email': 'admin@test.com', 'password': 'admin123', 'is_staff': True, 'is_superuser': True},
    {'username': 'seller1', 'email': 'seller1@test.com', 'password': 'seller123', 'is_staff': True, 'groups': ['Operador']},
    {'username': 'seller2', 'email': 'seller2@test.com', 'password': 'seller123', 'is_staff': True, 'groups': ['Operador']},
]

for user_data in users_data:
    groups = user_data.pop('groups', [])
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults=user_data
    )
    if created:
        user.set_password(user_data['password'])
        user.save()
        for group_name in groups:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        print(f"✅ Usuario {user.username} creado")
    else:
        print(f"⏭️ Usuario {user.username} ya existe")
```

Ejecuta:

```bash
python create_test_users.py
```

---

## Testing y Debugging

### P7: ¿Por qué mis tests fallan con "django.db.utils.ProgrammingError"?

**Respuesta:**

Las migraciones no se ejecutaron en la BD de test.

**Solución:**

```bash
python manage.py migrate
python manage.py test
```

Django crea automáticamente una BD de test para cada test run y la destruye después.

---

### P8: ¿Cómo debuggeo un test que falla?

**Respuesta:**

Opción 1: Añade prints:

```python
def test_something(self):
    result = my_function()
    print(f"DEBUG: result = {result}")
    self.assertEqual(result, expected)
```

Ejecuta el test con `-v 2`:

```bash
python manage.py test my_test -v 2
```

Opción 2: Usa debugger:

```python
import pdb

def test_something(self):
    result = my_function()
    pdb.set_trace()  # Se pausa aquí
    self.assertEqual(result, expected)
```

Opción 3: Usa pytest con breakpoint:

```python
def test_something():
    result = my_function()
    breakpoint()  # Se pausa aquí
    assert result == expected
```

---

### P9: ¿Cómo limpio el cache de tests?

**Respuesta:**

Los tests de Django usan transacciones que se hacen rollback automáticamente, así que no hay "cache" de tests persistente.

Si usas Redis para cache en desarrollo:

```bash
redis-cli FLUSHALL
```

---

### P10: ¿Cómo corro un test con una configuración diferente?

**Respuesta:**

Usa `@override_settings`:

```python
from django.test import override_settings

class MyTest(TestCase):
    @override_settings(DEBUG=False)
    def test_production_behavior(self):
        # Este test se ejecuta con DEBUG=False
        pass
```

---

## Deployment y Producción

### P11: ¿Qué debo verificar antes de hacer deploy?

**Respuesta:**

Checklist pre-producción:

```bash
# 1. Verificar que no hay errores
python manage.py check

# 2. Correr tests
python manage.py test

# 3. Verificar coverage
coverage run --source='.' manage.py test
coverage report --fail-under=80

# 4. Recolectar static files
python manage.py collectstatic --noinput

# 5. Hacer backup de BD
pg_dump -U user -h localhost erp_production > backup_before_deploy.sql

# 6. Verificar migraciones
python manage.py showmigrations

# 7. Verificar variables de entorno
cat .env | grep -E 'SECRET_KEY|DEBUG|ALLOWED_HOSTS|DATABASE_URL'
```

Checklist adicional:

- [ ] DEBUG=False
- [ ] SECRET_KEY única y fuerte
- [ ] ALLOWED_HOSTS correcto (sin *, con dominios reales)
- [ ] HTTPS/SSL configurado
- [ ] Backups automáticos configurados
- [ ] Logs configurados
- [ ] Health checks configurados
- [ ] Equipo notificado

---

### P12: ¿Cómo veo los logs en producción?

**Respuesta:**

```bash
# Django logs
sudo tail -f /var/log/erp/django.log

# Auditoría logs
sudo tail -f /var/log/erp/audit.log

# Gunicorn error logs
sudo tail -f /var/log/erp/gunicorn-error.log

# Gunicorn access logs
sudo tail -f /var/log/erp/gunicorn-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Buscar errores específicos
sudo grep ERROR /var/log/erp/django.log | tail -20
```

---

### P13: ¿Cómo hago un rollback de una migración en producción?

**Respuesta:**

**Opción 1: Revertir la última migración**

```bash
# Ver migraciones
python manage.py showmigrations sales

# Revertir a migración anterior
python manage.py migrate sales 0002
# (donde 0002 es la migración anterior a la que quieres revertir)

# Aplicar nuevamente después de arreglarlo
python manage.py migrate sales
```

**Opción 2: Rollback de BD desde backup**

```bash
# Restaurar backup
gunzip < backup_before_deploy.sql.gz | psql -U erp_user erp_production

# Verificar estado
python manage.py showmigrations
```

---

### P14: ¿Cómo redimensiono la BD o limpio espacio?

**Respuesta:**

```bash
# Ver tamaño de la BD
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('erp_production'));"

# Ver tamaño de tablas
sudo -u postgres psql -d erp_production -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema') ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# VACUUM limpia espacio no usado
sudo -u postgres psql -d erp_production -c "VACUUM ANALYZE;"
```

---

## Seguridad y Permisos

### P15: Usuario bloqueado por rate limiting de login, ¿cómo lo desbloqueo?

**Respuesta:**

El bloqueo dura 15 minutos automáticamente. Para desbloquearlo manualmente:

```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from core.services import UserService
>>> User = get_user_model()
>>> user = User.objects.get(username='blocked_user')
>>> user.failed_login_attempts = 0  # Reset contador (si existe)
>>> user.save()
```

O usa la BD directamente:

```bash
sudo -u postgres psql -d erp_production
# Si existe una tabla de intentos fallidos
DELETE FROM auth_failed_login_attempts WHERE user_id = 5;
```

---

### P16: ¿Cómo reseteo la contraseña de un usuario?

**Respuesta:**

**Opción 1: Como admin (en el admin)**

```
1. Ve a /admin/
2. Busca el usuario
3. Click en "Set password"
4. Ingresa nueva contraseña
5. Click "Save"
```

**Opción 2: Por shell**

```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='juan')
>>> user.set_password('nueva-contraseña')
>>> user.save()
>>> print("Contraseña reseteada")
```

**Opción 3: Comando custom**

```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='juan@example.com')
>>> from django.contrib.auth.tokens import default_token_generator
>>> token = default_token_generator.make_token(user)
>>> print(f"Reset token: {token}")
# Luego el usuario usa el enlace de reset
```

---

### P17: ¿Cómo cambio el SECRET_KEY en producción?

**Respuesta:**

**Advertencia:** Esto invalida todas las sesiones activas.

```bash
# 1. Generar nueva SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 2. Actualizar .env
# Edita .env con la nueva KEY

# 3. Hacer backup
pg_dump -U user -h localhost erp_production > backup_before_key_change.sql

# 4. Reiniciar servicio
sudo systemctl restart erp-gunicorn

# 5. Verificar que está funcionando
curl https://erp.tuempresa.com/dashboard/
```

---

### P18: ¿Cómo audito qué usuario hizo qué cambio?

**Respuesta:**

Accede a la tabla `AuditLog`:

```bash
python manage.py shell
>>> from core.models import AuditLog
>>> # Ver últimas 10 acciones
>>> AuditLog.objects.order_by('-timestamp')[:10]
>>> # Ver acciones de un usuario
>>> AuditLog.objects.filter(user__username='juan')[:10]
>>> # Ver acciones sobre un modelo
>>> AuditLog.objects.filter(model_name='Sale').order_by('-timestamp')[:10]
```

O vía admin:

```
1. Ve a /admin/
2. Click en "Audit logs"
3. Filtra por usuario, acción, fecha
```

---

## Performance y Cache

### P19: ¿Por qué los parámetros del sistema no se actualizan inmediatamente?

**Respuesta:**

Los parámetros se cachean por 1 hora para performance.

```python
# En settings.py
CACHE_TIMEOUT = 3600  # 1 hora
```

Para que se actualice inmediatamente:

**Opción 1: Borrar el cache manualmente**

```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
>>> print("Cache limpiado")
```

**Opción 2: Acceder a la BD directamente (bypassing cache)**

```bash
python manage.py shell
>>> from core.models import SystemParameter
>>> param = SystemParameter.objects.get(key='MY_PARAM')
>>> param.value = 'new_value'
>>> param.save()
# Luego limpiar cache
>>> from django.core.cache import cache
>>> cache.delete(f'system_parameter_MY_PARAM')
```

---

### P20: ¿Cómo limpio el cache completo?

**Respuesta:**

```bash
# Si usas Redis
redis-cli FLUSHALL

# Si usas LocMem (desarrollo)
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Si usas Memcached
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

---

### P21: ¿Cómo mido la performance de mis vistas?

**Respuesta:**

Opción 1: Usa Django Debug Toolbar (desarrollo):

```bash
pip install django-debug-toolbar
```

En `erp/settings.py`:

```python
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

En `erp/urls.py`:

```python
if DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

Opción 2: Usa herramienta de profiling:

```bash
pip install django-silk
```

Opción 3: Log de queries:

```python
from django.db import connection, reset_queries
from django.conf import settings

if settings.DEBUG:
    reset_queries()
    # ... tu código ...
    print(f"Queries ejecutadas: {len(connection.queries)}")
    for query in connection.queries:
        print(f"  {query['time']}s: {query['sql'][:100]}")
```

---

## Errores Comunes

### P22: Error "ModuleNotFoundError: No module named 'django'"

**Causa:** Entorno virtual no activado o dependencias no instaladas.

**Solución:**

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

---

### P23: Error "ConnectionRefusedError: [Errno 111] Connection refused"

**Causa:** PostgreSQL o Redis no está corriendo.

**Solución:**

```bash
# Para PostgreSQL
sudo systemctl status postgresql
sudo systemctl start postgresql

# Para Redis (si lo usas)
sudo systemctl status redis-server
sudo systemctl start redis-server
```

---

### P24: Error "CSRF token missing or incorrect"

**Causa:** CSRF_TRUSTED_ORIGINS no configurado o formulario sin token.

**Solución:**

```bash
# 1. Verificar .env
CSRF_TRUSTED_ORIGINS=https://erp.tuempresa.com,https://www.erp.tuempresa.com

# 2. En templates, asegurate de incluir el token
{% csrf_token %}

# 3. En AJAX requests, incluir header
headers: {
    'X-CSRFToken': getCookie('csrftoken')
}
```

---

### P25: Error "500 Internal Server Error" en producción

**Solución:**

1. Ver logs:

```bash
sudo tail -f /var/log/erp/django.log
sudo tail -f /var/log/erp/gunicorn-error.log
```

2. Verificar que DEBUG=False en .env:

```bash
cat .env | grep DEBUG
```

3. Reiniciar servicio:

```bash
sudo systemctl restart erp-gunicorn
```

4. Si persiste, hacer rollback:

```bash
# Revertir cambios de código
git revert HEAD

# O restaurar desde backup
pg_dump backup.sql | psql erp_production
```

---

## Recursos Útiles

- [Django Troubleshooting](https://docs.djangoproject.com/en/6.0/faq/)
- [PostgreSQL FAQ](https://www.postgresql.org/docs/current/faq.html)
- [Django Security](https://docs.djangoproject.com/en/6.0/topics/security/)

---

## Contribuir a este FAQ

Si encuentras un problema no documentado aquí:

1. Resuélvelo
2. Documenta la pregunta y respuesta
3. Agregalo a este archivo
4. Commit y push
