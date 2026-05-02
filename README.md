# ERP Django

Sistema ERP modular desarrollado con Django.

## 📖 Documentación

**Índice central:** [`documentacion/INDEX.md`](documentacion/INDEX.md) - Navegación completa de toda la documentación.

### Guías principales (2026-05-02)

| Guía | Propósito | Audiencia | Tiempo |
|------|----------|-----------|--------|
| [GUIA_DESARROLLO.md](documentacion/GUIA_DESARROLLO.md) | Crear nuevos módulos paso a paso | Devs | 30 min |
| [GUIA_TESTING.md](documentacion/GUIA_TESTING.md) | Tests unitarios e integración | Devs | 30 min |
| [GUIA_DEPLOYMENT.md](documentacion/GUIA_DEPLOYMENT.md) | Deploy a producción | DevOps | 45 min |
| [REFERENCIA_ENDPOINTS.md](documentacion/REFERENCIA_ENDPOINTS.md) | Todos los endpoints disponibles | Todos | 10 min |
| [FAQ_TROUBLESHOOTING.md](documentacion/FAQ_TROUBLESHOOTING.md) | Preguntas frecuentes y soluciones | Todos | Variable |

### Documentación de referencia

- [ARQUITECTURA_Y_ESTADO_ACTUAL.md](documentacion/ARQUITECTURA_Y_ESTADO_ACTUAL.md) - Patrón arquitectónico, estado del proyecto
- [IMPLEMENTACION_SEGURIDAD_Y_ACCESOS.md](documentacion/IMPLEMENTACION_SEGURIDAD_Y_ACCESOS.md) - Detalles de seguridad
- [IMPLEMENTACION_RESET_PASSWORD.md](documentacion/IMPLEMENTACION_RESET_PASSWORD.md) - Flujo de reset de contraseña
- [REVISION_TECNICA_2026-04-11.md](documentacion/REVISION_TECNICA_2026-04-11.md) - Problemas resueltos, recomendaciones

## Estado actual

El proyecto tiene un módulo funcional y varios módulos base preparados para crecer:

- `core`: implementado y operativo. Incluye autenticación, gestión de usuarios, roles, permisos, auditoría y parámetros del sistema.
- `masters`, `purchases`, `sales`, `inventory`, `accounting`, `reports`: apps scaffolded, listos para implementar siguiendo [`GUIA_DESARROLLO.md`](documentacion/GUIA_DESARROLLO.md).

## Arquitectura

El sistema sigue una arquitectura modular por dominio. El patrón de referencia está implementado en `core`:

- `models/`: entidades y modelos compartidos
- `services/`: lógica de negocio
- `forms/`: validaciones y formularios
- `views/`: vistas basadas en clases
- `templates/`: interfaz de usuario

Ver [`ARQUITECTURA_Y_ESTADO_ACTUAL.md`](documentacion/ARQUITECTURA_Y_ESTADO_ACTUAL.md) para detalles.

## Requisitos

- Python 3.12+
- Django 6.x
- Base de datos configurable por `DATABASE_URL`

## Instalación

1. Clonar el repositorio.
2. Crear el entorno virtual.
3. Instalar dependencias con `pip install -r requirements.txt`.
4. Crear el archivo `.env` a partir de `.env.example`.
5. Ejecutar migraciones con `python manage.py migrate`.
6. Crear superusuario con `python manage.py createsuperuser`.
7. Levantar el servidor con `python manage.py runserver`.

## Variables de entorno

Variables mínimas:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
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

## Desarrollo

Para crear nuevos módulos, consulta [`GUIA_DESARROLLO.md`](documentacion/GUIA_DESARROLLO.md).

Convenciones del proyecto:

- arquitectura modular por dominios (ver [`ARQUITECTURA_Y_ESTADO_ACTUAL.md`](documentacion/ARQUITECTURA_Y_ESTADO_ACTUAL.md))
- lógica de negocio centralizada en servicios
- vistas basadas en clases (CBV)
- documentación en español
- tests unitarios en paquetes `tests/` por app
- cobertura de código mínima: 80%

Para escribir tests, consulta [`GUIA_TESTING.md`](documentacion/GUIA_TESTING.md).

## Comandos útiles

```bash
python manage.py check
python manage.py test
python manage.py makemigrations
python manage.py migrate
python manage.py create_default_roles
```

## Observaciones importantes

- No mezcles `tests.py` con paquete `tests/` en la misma app
- Solo `core` tiene funcionalidad implementada; el resto está scaffolded y listo para desarrollar
- Antes de hacer deploy, consulta [`GUIA_DEPLOYMENT.md`](documentacion/GUIA_DEPLOYMENT.md)
- Si tienes problemas, consulta [`FAQ_TROUBLESHOOTING.md`](documentacion/FAQ_TROUBLESHOOTING.md)

## Licencia

Este proyecto está bajo la Licencia MIT.