# Arquitectura y Estado Actual del ERP

Fecha: 2026-05-02

## 1) Objetivo del repositorio
Este repositorio implementa un ERP modular en Django. En el estado actual, los dominios funcionales activos son `core` y `sales`, mientras que el resto de las apps existen como base estructural para futuras iteraciones.

## 2) Estado por módulo

### Implementado
- `core`
  - autenticación y login con rate limit básico
  - logout por POST
  - recuperación y cambio de contraseña
  - ABM de usuarios
  - ABM de roles y permisos
  - parámetros del sistema
  - auditoría de eventos

- `sales`
  - modelo de ventas (`Sale`) e ítems (`SaleItem`)
  - lógica de negocio en `SaleService`
  - formularios y validaciones de alta/edición
  - vistas CRUD con control de acceso por staff/permisos
  - templates web para listado, detalle, formulario y baja lógica
  - integración en admin y barra de navegación
  - suite de tests de modelos, servicios, formularios y vistas

### Scaffold pendiente de implementación
- `masters`
- `purchases`
- `inventory`
- `accounting`
- `reports`

Estas apps están registradas en `INSTALLED_APPS`, pero hoy no contienen lógica de negocio implementada.

## 3) Patrón arquitectónico vigente

El patrón real del proyecto se observa en `core` y se aplica en `sales`:

- `models/base.py`: modelo base reutilizable con `created_at`, `updated_at` e `is_active`
- `models/*.py`: entidades del dominio
- `services/*.py`: reglas de negocio y operaciones de aplicación
- `forms/*.py`: validaciones de entrada y formularios de administración
- `views/*.py`: vistas basadas en clases, con mixins de seguridad y auditoría
- `templates/core/*.html`: interfaz de usuario del dominio

## 4) Convenciones recomendadas para nuevas apps

Para mantener consistencia con `core`, cada nueva app debería seguir esta estructura:

```text
app/
  forms/
    __init__.py
    entidad_form.py
  models/
    __init__.py
    entidad.py
  services/
    __init__.py
    entidad_service.py
  views/
    __init__.py
    entidad_views.py
  tests/
    __init__.py
    test_entidad.py
  templates/app/
    entidad_list.html
    entidad_form.html
    entidad_detail.html
```

Reglas de implementación:

- no duplicar `tests.py` si la app usa el paquete `tests/`
- concentrar lógica de negocio en `services/`
- usar `BaseModel` para entidades persistentes del ERP cuando aplique
- mantener vistas CBV y validaciones en formularios
- documentar en español las decisiones funcionales y técnicas relevantes

## 5) Configuración y entorno

El proyecto depende de variables de entorno leídas desde `.env`.

Variables mínimas:

- `SECRET_KEY`: clave secreta de Django
- `DEBUG`: modo debug
- `ALLOWED_HOSTS`: hosts permitidos separados por coma
- `DATABASE_URL`: conexión a base de datos

Variables operativas adicionales:

- `LANGUAGE_CODE`
- `TIME_ZONE`
- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`
- `LOGIN_MAX_ATTEMPTS`
- `LOGIN_LOCKOUT_SECONDS`
- `PASSWORD_RESET_TIMEOUT`

Se agregó `.env.example` como referencia mínima de configuración.

## 6) Testing

Estado actual:

- `core` contiene la suite principal de pruebas funcionales y de seguridad
- `sales` contiene suite de pruebas por componente (modelos, servicios, formularios, vistas)
- el resto de las apps tienen estructura para tests, pero todavía no tienen casos implementados

Comandos recomendados:

```bash
python manage.py check
python manage.py test
python manage.py test core
```

## 7) Riesgos conocidos

- solo `core` representa funcionalidad de negocio real hoy
- `sales` ya representa funcionalidad de negocio real junto con `core`
- el resto de los módulos no deben considerarse terminados ni productivos
- algunas deudas técnicas y hallazgos de revisión están documentados en `documentacion/REVISION_TECNICA_2026-04-11.md`