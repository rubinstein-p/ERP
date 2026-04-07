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

## 11) Actualizacion de documentacion (novedades no registradas previamente)
Se incorporaron funcionalidades que no estaban reflejadas en las secciones anteriores:

1. Matriz de permisos por modulo con asignacion rapida en ABM de roles:
  - Seleccion de modulos (`permission_modules`)
  - Nivel de acceso (`permission_level`: read/operate/manage)
  - Merge automatico con permisos manuales
  Archivos: `core/forms/role_form.py`, `core/services/role_service.py`, `core/templates/core/role_form.html`.

2. Semillas estandar de roles con comando de gestion:
  - Roles estandar: `Administrador`, `Operador`, `Auditor`, `Supervisor`
  - Modo extendido por dominio con `--extended`
  Archivo: `core/management/commands/create_default_roles.py`.

3. Matriz de roles estandar y extendida en servicio:
  - `get_standard_role_matrix()`
  - `get_extended_role_matrix()`
  - `create_standard_roles()`
  - `create_default_roles(include_extended=...)`
  Archivo: `core/services/role_service.py`.

4. Cobertura de pruebas ampliada:
  - pruebas de semillas estandar y modo extendido
  - pruebas de buscador/paginacion de roles
  Archivo: `core/tests.py`.

## 12) Revision de faltantes y brechas detectadas
Estado de revision del modulo seguridad/permisos/usuarios:

### Critico
1. La matriz de permisos por accion usa `codename__startswith` con una tupla de prefijos.
  En Django, ese lookup espera string y puede devolver permisos vacios para niveles `read/operate/manage`.
  Impacto: roles estandar (Operador/Auditor/Supervisor) pueden quedar sin permisos efectivos.
  Archivo: `core/services/role_service.py`.

### Alto
2. Logout por GET en vez de POST.
  Impacto: logout involuntario por enlaces externos/precarga (CSRF de cierre de sesion).
  Archivo: `core/views/user_views.py`.

3. Control de acceso basado en `is_staff` para ABM, pero sin `PermissionRequiredMixin` por accion.
  Impacto: falta granularidad por permiso para create/update/delete.
  Archivos: `core/views/user_views.py`, `core/views/role_views.py`.

### Medio
4. Falta politica de bloqueo por intentos fallidos de login y/o rate limiting.
  Impacto: expone a fuerza bruta.
  Archivo relacionado: `core/services/user_service.py`.

5. Falta flujo de recuperacion de contrasena (password reset) para operacion productiva.
  Impacto: dependencia de administracion manual.

6. Falta auditoria explicita de eventos de seguridad clave:
  - logout
  - cambio de contrasena
  - denegaciones de acceso

### Bajo
7. Mensajes de error capturan `Exception` generica en varias vistas.
  Impacto: menor trazabilidad y manejo menos fino de errores de negocio.
  Archivos: `core/views/user_views.py`, `core/views/role_views.py`.

## 13) Acciones recomendadas (orden sugerido)
1. Corregir filtro de prefijos de permisos en matriz por modulo.
2. Migrar logout a POST con confirmacion o boton protegido con CSRF.
3. Incorporar permisos por accion en vistas (listar/crear/editar/eliminar).
4. Implementar rate limiting o bloqueo por intentos.
5. Completar auditoria de eventos faltantes.
6. Agregar password reset y pruebas de integracion de seguridad.

## 14) Hardening aplicado despues de la revision
Se implementaron los puntos prioritarios y endurecimiento adicional:

1. Rate limiting en login:
  - configuracion por settings:
    - `LOGIN_MAX_ATTEMPTS` (default 5)
    - `LOGIN_LOCKOUT_SECONDS` (default 900)
  - bloqueo temporal al superar intentos
  - mensajes de intentos restantes y estado bloqueado
  Archivos: `erp/settings.py`, `core/services/user_service.py`, `core/views/user_views.py`.

2. Auditoria explicita de intentos fallidos de login:
  - nueva accion: `LOGIN_FAILED`
  - registro de razon (`invalid_credentials` / `rate_limited`), IP y user agent
  Archivos: `core/models/audit.py`, `core/services/user_service.py`.

3. Auditoria explicita de accesos denegados:
  - nueva accion: `ACCESS_DENIED`
  - mixin `PermissionAuditRequiredMixin` para registrar faltas de permiso
  - `StaffRequiredMixin` tambien audita denegaciones
  Archivos: `core/views/mixins.py`, `core/views/user_views.py`, `core/views/role_views.py`.

4. Logout endurecido:
  - logout solo por POST
  - GET retorna 405
  - navbar actualizada con formulario POST + CSRF
  - auditoria de `LOGOUT`
  Archivos: `core/views/user_views.py`, `templates/components/navbar.html`.

5. Auditoria de cambio de contrasena:
  - nueva accion: `PASSWORD_CHANGE`
  - registro al completar PasswordChangeView
  Archivo: `core/views/user_views.py`.

6. Permisos granulares por accion en ABM:
  - Usuarios: `core.view_user`, `core.add_user`, `core.change_user`, `core.delete_user`
  - Roles: `auth.view_group`, `auth.add_group`, `auth.change_group`, `auth.delete_group`
  Archivos: `core/views/user_views.py`, `core/views/role_views.py`.

7. Correccion de matriz de permisos por modulo:
  - reemplazo de filtro incorrecto por `Q()` combinado por prefijos
  - ajuste de roles estandar para incluir base de Core y evitar perfiles vacios
  Archivo: `core/services/role_service.py`.

## 15) Pruebas agregadas para hardening
Se incorporaron y validaron pruebas para:
- bloqueo por intentos fallidos (`LoginRateLimitTest`)
- auditoria de login fallido (`LOGIN_FAILED`)
- auditoria de acceso denegado (`ACCESS_DENIED`)
- seguridad de logout por POST (`LogoutSecurityTest`)

Archivo: `core/tests.py`.

## 16) Middleware de correlacion por request
Se agrego middleware de trazabilidad para correlacionar eventos de auditoria por request:

1. `RequestIdMiddleware`:
  - genera un `request_id` UUID por request
  - expone header de respuesta `X-Request-ID`
  - inyecta `request.request_id` para consumo interno

2. Contexto por request:
  - `core/request_context.py` usa `ContextVar` para almacenar el `request_id` activo

3. Integracion automatica en auditoria:
  - `AuditLog.save()` agrega `request_id` en `changes` cuando existe contexto activo
  - evita modificar manualmente cada punto de logging

Archivos:
- `core/middleware.py`
- `core/request_context.py`
- `core/models/audit.py`
- `erp/settings.py`

Pruebas de correlacion:
- validacion de header `X-Request-ID`
- validacion de `changes.request_id` en `LOGIN_FAILED` y `ACCESS_DENIED`
