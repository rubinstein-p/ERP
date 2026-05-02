# Referencia de Endpoints: API y Rutas del ERP

Fecha: 2026-05-02

## Introducción

Esta es una referencia completa de todos los endpoints disponibles en el ERP Django. Cada endpoint lista: URL, método HTTP, autenticación requerida, descripción y permisos.

**Nota:** `<id>` representa el identificador numérico del objeto.

---

## Endpoints Públicos

### Home

| Método | URL | Autenticación | Descripción |
|--------|-----|---------------|-----------|
| GET | `/` | No | Página de inicio pública |

**Ejemplo de respuesta:**
```html
<!-- Página de bienvenida con opción de login -->
```

---

## Endpoints de Autenticación

### Login

| Método | URL | Autenticación | Descripción |
|--------|-----|---------------|-----------|
| GET | `/login/` | No | Formulario de login |
| POST | `/login/` | No | Procesar login |

**Parámetros POST:**
```json
{
  "username": "usuario@example.com",
  "password": "tu-contraseña",
  "remember_me": false
}
```

**Respuesta exitosa:** Redirección a `/dashboard/` con sesión iniciada

**Respuesta error:** `400 Bad Request` si credenciales son inválidas

**Rate limiting:** Máximo 5 intentos fallidos, bloqueo de 15 minutos

---

### Logout

| Método | URL | Autenticación | Descripción |
|--------|-----|---------------|-----------|
| POST | `/logout/` | Sí | Cerrar sesión |

**Respuesta:** Redirección a `/login/`

---

### Password Reset - Solicitar

| Método | URL | Autenticación | Descripción |
|--------|-----|---------------|-----------|
| GET | `/password-reset/` | No | Formulario de solicitud |
| POST | `/password-reset/` | No | Procesar solicitud |

**Parámetros POST:**
```json
{
  "email": "usuario@example.com"
}
```

**Respuesta:** Redirección a `/password-reset/done/` (se envía email)

---

### Password Reset - Confirmación

| Método | URL | Autenticación | Descripción |
|--------|-----|---------------|-----------|
| GET | `/password-reset/confirm/<uidb64>/<token>/` | No | Formulario de nueva contraseña |
| POST | `/password-reset/confirm/<uidb64>/<token>/` | No | Procesar nueva contraseña |

**Parámetros POST:**
```json
{
  "new_password1": "nueva-contraseña-segura",
  "new_password2": "nueva-contraseña-segura"
}
```

**Respuesta:** Redirección a `/password-reset/complete/`

---

## Endpoints de Dashboard

### Dashboard

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/dashboard/` | Sí | Panel principal del usuario | Autenticado |

**Respuesta HTTP 200:**
```json
{
  "user": {
    "id": 1,
    "username": "usuario",
    "email": "usuario@example.com",
    "is_staff": true
  },
  "recent_activity": [],
  "system_stats": {
    "total_users": 5,
    "total_sales": 25,
    "total_parameters": 10
  }
}
```

**Respuesta HTTP 302:** Si no está autenticado, redirección a login

---

## Endpoints de Usuarios (ABM)

### Listar Usuarios

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/users/` | Sí | Listar todos los usuarios | `is_staff` o permiso `view_user` |

**Parámetros de query:**
```
GET /users/?search=juan&status=active&page=1&page_size=25
```

- `search`: Búsqueda por username, email, nombre, apellido
- `status`: `active`, `inactive`, `all` (por defecto `all`)
- `page`: Número de página (default 1)
- `page_size`: Cantidad por página (default 25)

**Respuesta HTTP 200:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "juan",
      "email": "juan@example.com",
      "first_name": "Juan",
      "last_name": "Pérez",
      "is_active": true,
      "is_staff": true,
      "created_at": "2026-04-01T10:30:00Z"
    }
  ]
}
```

---

### Ver Detalle de Usuario

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/users/<id>/` | Sí | Ver detalles de un usuario | `is_staff` o es el usuario mismo |

**Respuesta HTTP 200:**
```json
{
  "id": 1,
  "username": "juan",
  "email": "juan@example.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+54 9 123 456789",
  "department": "Ventas",
  "employee_id": "EMP-001",
  "is_active": true,
  "is_staff": true,
  "is_superuser": false,
  "groups": [
    {"id": 1, "name": "Operador"}
  ],
  "user_permissions": [
    {"id": 1, "codename": "add_sale", "name": "Can add sale"}
  ],
  "created_at": "2026-04-01T10:30:00Z",
  "updated_at": "2026-04-15T14:45:00Z"
}
```

---

### Crear Usuario

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/users/create/` | Sí | Formulario de creación | `is_staff` o permiso `add_user` |
| POST | `/users/create/` | Sí | Crear nuevo usuario | `is_staff` o permiso `add_user` |

**Parámetros POST:**
```json
{
  "username": "nuevo_usuario",
  "email": "nuevo@example.com",
  "first_name": "Nuevo",
  "last_name": "Usuario",
  "password": "contraseña-segura",
  "phone": "+54 9 123 456789",
  "department": "Ventas",
  "employee_id": "EMP-002",
  "is_staff": false,
  "groups": [1, 2],
  "user_permissions": []
}
```

**Respuesta HTTP 201:** Usuario creado, redirección a `/users/`

**Respuesta HTTP 400:** Errores de validación

---

### Editar Usuario

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/users/<id>/edit/` | Sí | Formulario de edición | `is_staff` o permiso `change_user` |
| POST | `/users/<id>/edit/` | Sí | Actualizar usuario | `is_staff` o permiso `change_user` |

**Parámetros POST:** (igual a Crear Usuario)

**Respuesta HTTP 200:** Usuario actualizado, redirección a `/users/<id>/`

---

### Eliminar Usuario (Soft Delete)

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/users/<id>/delete/` | Sí | Confirmación de eliminación | `is_staff` o permiso `delete_user` |
| POST | `/users/<id>/delete/` | Sí | Marcar como inactivo | `is_staff` o permiso `delete_user` |

**Respuesta HTTP 302:** Usuario desactivado (no eliminado de BD), redirección a `/users/`

---

### Cambiar Contraseña (por Admin)

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/users/<id>/password/` | Sí | Formulario | `is_staff` o permiso `change_user` |
| POST | `/users/<id>/password/` | Sí | Cambiar contraseña | `is_staff` o permiso `change_user` |

**Parámetros POST:**
```json
{
  "new_password": "nueva-contraseña"
}
```

---

## Endpoints de Perfil del Usuario

### Ver Mi Perfil

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/profile/` | Sí | Ver mi perfil | Autenticado |

**Respuesta HTTP 200:** (igual a `/users/<id>/` del usuario actual)

---

### Cambiar Mi Contraseña

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/profile/password/` | Sí | Formulario | Autenticado |
| POST | `/profile/password/` | Sí | Cambiar contraseña | Autenticado |

**Parámetros POST:**
```json
{
  "old_password": "contraseña-actual",
  "new_password1": "nueva-contraseña",
  "new_password2": "nueva-contraseña"
}
```

---

## Endpoints de Roles (ABM)

### Listar Roles

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/roles/` | Sí | Listar todos los roles | `is_staff` o permiso `view_group` |

**Parámetros de query:**
```
GET /roles/?search=operador&permission=add_sale&page=1
```

- `search`: Búsqueda por nombre de rol
- `permission`: Filtrar por permiso (codename)
- `page`: Número de página

**Respuesta HTTP 200:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Administrador",
      "permissions": [1, 2, 3, ...],
      "user_count": 2
    }
  ]
}
```

---

### Ver Detalle de Rol

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/roles/<id>/` | Sí | Ver detalles del rol | `is_staff` o permiso `view_group` |

**Respuesta HTTP 200:**
```json
{
  "id": 1,
  "name": "Operador",
  "permissions": [
    {"id": 1, "codename": "add_sale", "name": "Can add sale"},
    {"id": 2, "codename": "change_sale", "name": "Can change sale"}
  ],
  "users": [
    {"id": 1, "username": "juan"},
    {"id": 2, "username": "maria"}
  ]
}
```

---

### Crear Rol

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/roles/create/` | Sí | Formulario | `is_staff` o permiso `add_group` |
| POST | `/roles/create/` | Sí | Crear rol | `is_staff` o permiso `add_group` |

**Parámetros POST:**
```json
{
  "name": "Nuevo Rol",
  "permissions": [1, 2, 3],
  "permission_modules": ["core", "sales"],
  "permission_level": "operate"
}
```

---

### Editar Rol

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/roles/<id>/edit/` | Sí | Formulario | `is_staff` o permiso `change_group` |
| POST | `/roles/<id>/edit/` | Sí | Actualizar rol | `is_staff` o permiso `change_group` |

---

### Eliminar Rol

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/roles/<id>/delete/` | Sí | Confirmación | `is_staff` o permiso `delete_group` |
| POST | `/roles/<id>/delete/` | Sí | Eliminar rol | `is_staff` o permiso `delete_group` |

**Respuesta HTTP 302:** Rol eliminado, redirección a `/roles/`

---

## Endpoints de Parámetros del Sistema

### Listar Parámetros

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/parameters/` | Sí | Listar parámetros | `is_staff` o permiso `view_systemparameter` |

**Parámetros de query:**
```
GET /parameters/?search=email&category=email&page=1
```

- `search`: Búsqueda por clave
- `category`: Filtrar por categoría

**Respuesta HTTP 200:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "key": "EMAIL_HOST",
      "value": "smtp.gmail.com",
      "parameter_type": "STRING",
      "category": "email",
      "description": "Host SMTP para envío de emails",
      "is_system": true
    }
  ]
}
```

---

### Ver Detalle de Parámetro

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/parameters/<id>/` | Sí | Ver parámetro | `is_staff` o permiso `view_systemparameter` |

---

### Crear Parámetro

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| POST | `/parameters/create/` | Sí | Crear parámetro | `is_staff` o permiso `add_systemparameter` |

**Parámetros POST:**
```json
{
  "key": "NUEVO_PARAMETRO",
  "value": "valor",
  "parameter_type": "STRING",
  "category": "custom",
  "description": "Descripción del parámetro",
  "is_system": false
}
```

---

### Editar Parámetro

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| POST | `/parameters/<id>/edit/` | Sí | Actualizar parámetro | `is_staff` o permiso `change_systemparameter` |

---

### Eliminar Parámetro

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| POST | `/parameters/<id>/delete/` | Sí | Eliminar parámetro | `is_staff` o permiso `delete_systemparameter` |

---

### Inicializar Parámetros

| Método | URL | Autenticación | Descripción | Permisos |
|--------|-----|---------------|-----------|-----------|
| GET | `/parameters/initialize/` | Sí | Formulario | `is_superuser` |
| POST | `/parameters/initialize/` | Sí | Crear parámetros por defecto | `is_superuser` |

**Respuesta HTTP 200:**
```json
{
  "message": "Parámetros del sistema inicializados",
  "created": 8,
  "updated": 2
}
```

---

## Códigos de Estado HTTP

| Código | Significado | Causa Común |
|--------|------------|-----------|
| **200** | OK | Solicitud exitosa |
| **201** | Created | Recurso creado exitosamente |
| **302** | Found (Redirect) | Redirección (después de crear/editar/eliminar) |
| **400** | Bad Request | Datos inválidos, validación fallida |
| **401** | Unauthorized | No autenticado |
| **403** | Forbidden | Autenticado pero sin permisos |
| **404** | Not Found | Recurso no existe |
| **429** | Too Many Requests | Rate limit excedido (login) |
| **500** | Internal Server Error | Error en el servidor |

---

## Permisos por Módulo

### Core

| Permiso | Descripción |
|---------|-----------|
| `view_user` | Ver usuarios |
| `add_user` | Crear usuarios |
| `change_user` | Editar usuarios |
| `delete_user` | Eliminar usuarios |
| `view_group` | Ver roles |
| `add_group` | Crear roles |
| `change_group` | Editar roles |
| `delete_group` | Eliminar roles |
| `view_systemparameter` | Ver parámetros |
| `add_systemparameter` | Crear parámetros |
| `change_systemparameter` | Editar parámetros |
| `delete_systemparameter` | Eliminar parámetros |

### Sales (cuando esté implementado)

| Permiso | Descripción |
|---------|-----------|
| `view_sale` | Ver ventas |
| `add_sale` | Crear ventas |
| `change_sale` | Editar ventas |
| `delete_sale` | Eliminar ventas |

---

## Ejemplo de Integración (cURL)

### Hacer login

```bash
curl -X POST http://localhost:8000/login/ \
  -d "username=usuario&password=contraseña&remember_me=false" \
  -c cookies.txt
```

### Listar usuarios (usando cookie de login)

```bash
curl -X GET http://localhost:8000/users/ \
  -b cookies.txt \
  -H "Accept: application/json"
```

### Crear usuario

```bash
curl -X POST http://localhost:8000/users/create/ \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo",
    "email": "nuevo@test.com",
    "password": "contraseña"
  }'
```

---

## Headers Recomendados

Incluye estos headers en requests:

```
X-Requested-With: XMLHttpRequest
Accept: application/json
Content-Type: application/json
X-Request-ID: <uuid generado por cliente>  # Para auditoría
```

---

## Rate Limiting

| Endpoint | Límite | Ventana |
|----------|--------|---------|
| `/login/` | 5 intentos | 15 minutos |
| Otros endpoints | No aplicable | - |

Después de 5 intentos fallidos de login, la cuenta se bloquea por 15 minutos.

---

## Próximas Adiciones

Cuando se implementen módulos, se agregarán endpoints:

- `/sales/` (Ventas)
- `/purchases/` (Compras)
- `/inventory/` (Inventario)
- `/accounting/` (Contabilidad)
- `/reports/` (Reportes)
