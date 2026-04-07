# ERP Django

Sistema de planificación de recursos empresariales (ERP) desarrollado con Django.

## Descripción

Este proyecto implementa un ERP modular con las siguientes funcionalidades:
- Gestión de usuarios y seguridad (Core)
- Maestros (clientes, proveedores, productos)
- Compras
- Ventas
- Inventario
- Contabilidad
- Reportes

## Arquitectura

El sistema sigue una arquitectura modular donde cada dominio es una app Django independiente:

- `core`: Seguridad, usuarios, auditoría, parámetros
- `masters`: Datos maestros (clientes, proveedores, productos, categorías)
- `purchases`: Gestión de compras y proveedores
- `sales`: Gestión de ventas y clientes
- `inventory`: Control de inventario y movimientos
- `accounting`: Contabilidad e integración financiera
- `reports`: Reportes y dashboards

## Requisitos

- Python 3.8+
- Django 6.0+
- PostgreSQL (producción) / SQLite (desarrollo)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd erp-django
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Ejecutar migraciones:
```bash
python manage.py migrate
```

6. Crear superusuario:
```bash
python manage.py createsuperuser
```

7. Ejecutar servidor de desarrollo:
```bash
python manage.py runserver
```

## Estructura del proyecto

```
erp/
├── manage.py
├── requirements.txt
├── .env
├── erp/                     # Configuración global
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                    # Seguridad y usuarios
├── masters/                 # Datos maestros
├── purchases/               # Compras
├── sales/                   # Ventas
├── inventory/              # Inventario
├── accounting/             # Contabilidad
├── reports/                # Reportes
├── templates/              # Plantillas globales
└── static/                 # Archivos estáticos
```

## Desarrollo

## Documentacion Tecnica

- Implementacion de seguridad y accesos: `documentacion/IMPLEMENTACION_SEGURIDAD_Y_ACCESOS.md`

### Convenciones
- Usar arquitectura modular por dominios
- Toda lógica de negocio en servicios
- Vistas basadas en clases (CBV)
- Tests unitarios obligatorios
- Documentación en español

### Comandos útiles

```bash
# Ejecutar tests
python manage.py test

# Crear nueva app
python manage.py startapp nueva_app

# Crear migraciones
python manage.py makemigrations

# Ejecutar migraciones
python manage.py migrate

# Ejecutar linter
flake8

# Formatear código
black .
isort .
```

## Contribución

1. Crear rama desde `develop`
2. Implementar cambios siguiendo la arquitectura
3. Escribir tests
4. Hacer pull request

## Licencia

Este proyecto está bajo la Licencia MIT.