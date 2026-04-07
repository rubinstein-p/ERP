# Implementacion Seguridad y Accesos

Fecha: 2026-04-07
Rama de trabajo: develop

## 1) Resumen ejecutivo
Durante esta iteracion se implemento y valido el modulo de seguridad con foco en:
- Gestion de usuarios (ABM)
- Gestion de roles/grupos y permisos (ABM)
- Control de acceso por perfil staff/superuser
- Auditoria de cambios criticos
- Inicializacion de roles principales del sistema
- Ajustes de configuracion base del proyecto (idioma, zona horaria y gitignore)

## 2) Cambios de configuracion base
### 2.1 .gitignore
Se creo y ajusto `.gitignore` para Django/Python incluyendo:
- cache y bytecode
- entornos virtuales (`.venv/`, `venv/`, `env/`, `ENV/`)
- secretos y `.env`
- artefactos de Django (`staticfiles/`, `media/`, logs)

Archivo:
- `.gitignore`

### 2.2 Internacionalizacion y zona horaria
Se corrigio `erp/settings.py` para leer valores como string desde entorno:
- `LANGUAGE_CODE = env('LANGUAGE_CODE', default='es-ar')`
- `TIME_ZONE = env('TIME_ZONE', default='America/Argentina/Tucuman')`

Archivo:
- `erp/settings.py`

## 3) Seguridad de acceso en vistas
Se incorporo mixin de control de acceso para pantallas administrativas:
- `StaffRequiredMixin`: permite acceso solo a usuarios autenticados staff o superuser.

Archivo:
- `core/views/mixins.py`

Aplicado en:
- ABM de usuarios
- ABM de parametros del sistema
- ABM de roles

## 4) Gestion de usuarios (ABM)
## 4.1 Backend
Se completo la gestion de usuarios con:
- alta, listado, detalle, edicion y baja logica
- filtros por estado (activos/inactivos/todos)
- busqueda por username, email, nombre, apellido y legajo
- soporte de grupos y permisos directos en alta/edicion
- soporte de flags de seguridad (`is_active`, `is_staff`, `is_superuser`)
- remember me en login (expiracion de sesion al cerrar navegador cuando no esta tildado)

Archivos:
- `core/views/user_views.py`
- `core/forms/user_form.py`
- `core/services/user_service.py`

## 4.2 Frontend
Se crearon las vistas de interfaz de usuarios respetando el estilo del dashboard (Bootstrap, cards, badges, botones y paleta existente):
- `core/templates/core/user_list.html`
- `core/templates/core/user_form.html`
- `core/templates/core/user_detail.html`
- `core/templates/core/user_confirm_delete.html`
- `core/templates/core/profile.html`
- `core/templates/core/password_change.html`

## 5) Gestion de roles/grupos y permisos (ABM visual)
## 5.1 Concepto funcional
En esta implementacion:
- Rol (termino funcional) = Grupo de Django (`auth.Group`)
- Los permisos se asignan al rol/grupo y los usuarios heredan permisos por pertenencia.

## 5.2 Backend
Se implemento servicio de roles con operaciones:
- listar roles
- crear rol con permisos
- editar rol y permisos
- eliminar rol
- inicializar roles principales

Archivos:
- `core/services/role_service.py`
- `core/forms/role_form.py`
- `core/views/role_views.py`
- `core/forms/__init__.py`
- `core/services/__init__.py`
- `core/views/__init__.py`

## 5.3 Frontend
Se implemento ABM visual de roles:
- listado
- detalle (permisos + usuarios asignados)
- alta/edicion
- confirmacion de eliminacion

Archivos:
- `core/templates/core/role_list.html`
- `core/templates/core/role_form.html`
- `core/templates/core/role_detail.html`
- `core/templates/core/role_confirm_delete.html`

## 5.4 Busqueda por permiso y paginacion avanzada
En listado de roles se agrego:
- busqueda por nombre de rol
- busqueda por permiso (nombre, codename, app_label)
- paginacion avanzada con:
  - tamano por pagina: 10/25/50/100
  - primera/anterior/siguiente/ultima
  - ventana numerica de paginas
  - persistencia de filtros al paginar

Archivos:
- `core/views/role_views.py`
- `core/templates/core/role_list.html`

## 6) Rutas de seguridad expuestas
Rutas de usuarios:
- `/users/`
- `/users/create/`
- `/users/<id>/`
- `/users/<id>/edit/`
- `/users/<id>/delete/`

Rutas de roles:
- `/roles/`
- `/roles/create/`
- `/roles/<id>/`
- `/roles/<id>/edit/`
- `/roles/<id>/delete/`

Archivo de rutas:
- `core/urls.py`

## 7) Navegacion
Se agregaron accesos en navbar para perfiles staff/superuser:
- Seguridad
- Roles

Archivo:
- `templates/components/navbar.html`

## 8) Inicializacion de roles principales
Se creo comando de gestion para crear/actualizar roles base:
- `python manage.py create_default_roles`

Archivo:
- `core/management/commands/create_default_roles.py`

Roles definidos por defecto:
- Administrador del Sistema
- Administrador de Seguridad
- Operador ERP
- Contador
- Auditor

Regla de permisos por rol definida en:
- `core/services/role_service.py` (`create_default_roles`)

## 9) Pruebas y validacion
Se agregaron y ejecutaron pruebas para:
- acceso de usuarios regulares vs staff
- alta/edicion/baja de roles
- filtros por permiso en listado de roles
- paginacion configurable por page size
- asignacion de grupos y permisos en usuarios

Archivo de pruebas:
- `core/tests.py`

Comandos de validacion ejecutados:
- `python manage.py check`
- `python manage.py test core.tests.UserPermissionsManagementTest`
- `python manage.py test core.tests.RoleManagementTest`
- `python manage.py test core.tests.UserPermissionsManagementTest core.tests.RoleManagementTest`

Resultado:
- checks sin issues
- tests ejecutados en verde

## 10) Estado actual y siguientes pasos sugeridos
Estado actual:
- Modulo de seguridad funcional con ABM de usuarios y roles
- Roles principales inicializados en base
- UI consistente con dashboard

Siguientes pasos recomendados:
1. Definir matriz fina de permisos por subproceso (compras, ventas, inventario, contabilidad).
2. Incorporar politica de bloqueo por intentos fallidos de login.
3. Completar auditoria de eventos de seguridad (logout, cambios de password, alta/baja de roles).
4. Agregar tests de integracion de flujo completo usuario + rol + acceso a vistas por permiso.
