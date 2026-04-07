# Instrucciones de Copilot para el proyecto ERP en Django

Estas instrucciones guían a los agentes definidos en `AGENTS.md` para trabajar dentro de este repositorio como un equipo de ingeniería senior especializado en Django, arquitectura modular y desarrollo de ERPs.

El objetivo es asegurar consistencia, escalabilidad, mantenibilidad y alineación con la arquitectura definida para el proyecto.

---

# 🧠 Agentes disponibles

Los agentes definidos en `AGENTS.md` deben trabajar de manera coordinada:

- **Copilot-ERP-Architect** → Diseña arquitectura, modelos, servicios y flujos.
- **Copilot-ERP-Developer** → Implementa código siguiendo la arquitectura.
- **Copilot-ERP-Reviewer** → Revisa código, detecta inconsistencias y sugiere mejoras.

Cada agente debe actuar dentro de su rol y respetar las reglas de este archivo.

---

# 📌 Estado del proyecto

Actualmente el repositorio contiene únicamente documentación en la carpeta `documentacion/`.

Archivos detectados:
- `documentacion/Blueprint.docx`
- `documentacion/documentacion.docx`
- `documentacion/PLANIFICACIÓN DEL PROYECTO ERP EN DJANGO.docx`

No existe aún un proyecto Django inicializado ni estructura de apps creada.

---

# 🛠️ Cómo deben ayudar los agentes

Cuando el usuario solicite desarrollo técnico, los agentes deben seguir este flujo:

## 1. Architect
- Confirmar requisitos funcionales.
- Validar reglas de negocio.
- Definir modelos, servicios, flujos y estructura.
- Asegurar que la solución respete la arquitectura modular.

## 2. Developer
- Implementar el código definido por el Architect.
- Crear modelos, servicios, vistas, formularios y tests.
- Mantener consistencia y buenas prácticas.

## 3. Reviewer
- Revisar el código generado.
- Detectar violaciones a la arquitectura.
- Sugerir mejoras de calidad, rendimiento y mantenibilidad.

---

# 🏗️ Estructura oficial del proyecto ERP

El ERP utiliza una arquitectura modular por dominios.  
Cada módulo es una app Django independiente y debe seguir esta estructura:

erp/
├── manage.py
├── requirements.txt
├── .env
│
├── erp/                     # Configuración global del proyecto
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── core/                    # Seguridad, usuarios, auditoría, parámetros
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── audit.py
│   │   └── parameters.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── audit_service.py
│   │   └── parameter_service.py
│   ├── forms/
│   │   ├── __init__.py
│   │   └── user_form.py
│   ├── views/
│   │   ├── __init__.py
│   │   └── user_views.py
│   ├── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_views.py
│
├── masters/                 # Maestros (clientes, proveedores, productos, etc.)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py
│   │   ├── customer.py
│   │   ├── supplier.py
│   │   └── category.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── product_service.py
│   │   ├── customer_service.py
│   │   └── supplier_service.py
│   ├── forms/
│   │   ├── __init__.py
│   │   └── product_form.py
│   ├── views/
│   │   ├── __init__.py
│   │   └── product_views.py
│   ├── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_views.py
│
├── purchases/               # Compras
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── purchase_order.py
│   │   ├── purchase_receipt.py
│   │   └── ap_invoice.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── purchase_order_service.py
│   │   └── receipt_service.py
│   ├── forms/
│   │   ├── __init__.py
│   ├── views/
│   │   ├── __init__.py
│   │   └── purchase_order_views.py
│   ├── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_views.py
│
├── sales/                   # Ventas
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── quotation.py
│   │   ├── sales_order.py
│   │   └── invoice.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── quotation_service.py
│   │   ├── sales_order_service.py
│   │   └── invoice_service.py
│   ├── forms/
│   │   ├── __init__.py
│   ├── views/
│   │   ├── __init__.py
│   │   └── sales_order_views.py
│   ├── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_views.py
│
├── inventory/               # Inventario
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── warehouse.py
│   │   ├── stock.py
│   │   └── movement.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── stock_service.py
│   │   └── movement_service.py
│   ├── forms/
│   │   ├── __init__.py
│   ├── views/
│   │   ├── __init__.py
│   │   └── stock_views.py
│   ├── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_views.py
│
├── accounting/              # Contabilidad
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── account.py
│   │   ├── journal_entry.py
│   │   └── journal_line.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── journal_entry_service.py
│   │   └── integration_service.py
│   ├── forms/
│   │   ├── __init__.py
│   ├── views/
│   │   ├── __init__.py
│   │   └── journal_entry_views.py
│   ├── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_views.py
│
├── reports/                 # Reportes y dashboards
│   ├── __init__.py
│   ├── apps.py
│   ├── views/
│   │   ├── __init__.py
│   │   └── dashboard_views.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── reporting_service.py
│   ├── urls.py
│   └── tests/
│       ├── __init__.py
│       └── test_views.py
│
├── templates/               # Plantillas globales
│   ├── base.html
│   ├── layout/
│   │   └── main_layout.html
│   └── components/
│       ├── navbar.html
│       ├── sidebar.html
│       └── messages.html
│
└── static/                  # Archivos estáticos
    ├── css/
    │   └── main.css
    ├── js/
    │   └── main.js
    └── img/


---

# 🧩 Reglas de arquitectura

### Estructura obligatoria por app
Cada app debe contener:
- `models/`
- `services/`
- `forms/`
- `views/`
- `urls.py`
- `tests/`

### Separación de responsabilidades
- **Models** → invariantes del dominio.  
- **Services** → TODA la lógica de negocio.  
- **Views** → orquestación, nunca lógica.  
- **Forms** → validaciones.  
- **Tests** → unitarios + integración.

### Interacción entre módulos
- `core` puede ser usado por todos.
- `masters` puede ser usado por purchases, sales, inventory, accounting.
- `purchases`, `sales` e `inventory` deben integrarse con `accounting` mediante servicios.
- `reports` solo puede leer datos.

### Consultas
- Usar siempre `select_related` y `prefetch_related`.

---

# 📚 Reglas para modelos
- Usar `BaseModel` con: `created_at`, `updated_at`, `is_active`.
- Usar `on_delete=models.PROTECT` salvo excepciones.
- Definir `__str__`.
- Definir `Meta` con `ordering`.
- No incluir lógica de negocio.

---

# ⚙️ Reglas para servicios
- Un archivo por concepto.
- No importar vistas.
- No acceder a `request`.
- Manejar validaciones y reglas de negocio.
- Ser testeables de forma aislada.

---

# 🖥️ Reglas para vistas
- Usar CBV.
- Usar `LoginRequiredMixin`.
- No incluir lógica de negocio.
- Delegar validaciones a forms o services.

---

# 🎨 Reglas para templates
- Usar Bootstrap 5.
- Usar `base.html`.
- Componentes en `templates/components/`.

---

# 🧪 Testing
- Cobertura mínima recomendada: **80%**.
- Tests unitarios para servicios.
- Tests de modelos.
- Tests de vistas.

---

# 📝 Documentación
- Cada módulo debe tener un README interno.
- Cada servicio debe documentar entradas, salidas y reglas.
- Los modelos deben documentar propósito y relaciones.

---

# 📌 Reglas de trabajo generales
- No asumir que existe un proyecto Django funcional si no se detecta.
- Confirmar antes de generar código nuevo.
- No modificar documentos sin aprobación.
- Explicar limitaciones cuando falte contexto.
- Priorizar respuestas en español.

---

# 💡 Sugerencias de uso
- "Crea los modelos del módulo masters."
- "Genera los servicios para órdenes de compra."
- "Diseña el flujo de ventas."
- "Implementa el módulo core."
- "Revisa este código y sugiere mejoras."

---

# 📎 Metadatos
Este archivo es la guía base para los agentes del proyecto ERP en Django.