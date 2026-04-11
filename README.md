# ERP Django

Sistema ERP modular desarrollado con Django.

## Estado actual

El proyecto tiene un módulo funcional y varios módulos base preparados para crecer:

- `core`: implementado y operativo. Incluye autenticación, gestión de usuarios, roles, permisos, auditoría y parámetros del sistema.
- `masters`, `purchases`, `sales`, `inventory`, `accounting`, `reports`: apps scaffolded, todavía sin modelos, servicios ni vistas de negocio implementadas.

## Arquitectura

El sistema sigue una arquitectura modular por dominio. El patrón de referencia está implementado en `core`:

- `models/`: entidades y modelos compartidos
- `services/`: lógica de negocio
- `forms/`: validaciones y formularios
- `views/`: vistas basadas en clases
- `templates/`: interfaz de usuario

La documentación ampliada de arquitectura, estado y convenciones está en:

- `documentacion/ARQUITECTURA_Y_ESTADO_ACTUAL.md`
- `documentacion/IMPLEMENTACION_SEGURIDAD_Y_ACCESOS.md`
- `documentacion/IMPLEMENTACION_RESET_PASSWORD.md`
- `documentacion/REVISION_TECNICA_2026-04-11.md`

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

Convenciones actuales del proyecto:

- arquitectura modular por dominios
- lógica de negocio en servicios
- vistas basadas en clases
- documentación en español
- tests centralizados en paquetes `tests/` por app cuando la app los necesite

## Comandos útiles

```bash
python manage.py check
python manage.py test
python manage.py makemigrations
python manage.py migrate
python manage.py create_default_roles
```

## Observaciones importantes

- La suite de tests del proyecto ya no debe mezclar `tests.py` con paquetes `tests/` dentro de la misma app.
- El único módulo con funcionalidad de negocio implementada hoy es `core`; el resto está documentado como roadmap técnico y no como funcionalidad terminada.

## Licencia

Este proyecto está bajo la Licencia MIT.