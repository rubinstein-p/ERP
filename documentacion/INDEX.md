# Documentación del ERP Django: Índice y Navegación

Fecha: 2026-05-02

## 🎯 Bienvenida

Bienvenido a la documentación del **ERP Django Modular**. Este índice te guiará a través de toda la documentación disponible.

---

## 📚 Documentación por Audiencia

### 👨‍💼 **Para Desarrolladores (todos los niveles)**

| Documento | Nivel | Tiempo | Propósito |
|-----------|-------|--------|----------|
| [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md) | Junior/Senior | 30 min | Crear nuevos módulos de negocio (paso a paso) |
| [GUIA_TESTING.md](GUIA_TESTING.md) | Intermedio/Senior | 30 min | Escribir tests, frameworks, patrones |
| [REFERENCIA_ENDPOINTS.md](REFERENCIA_ENDPOINTS.md) | Junior/Senior | 15 min | Listar todas las rutas y su documentación |
| [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md) | Junior/Senior | 15 min | Respuestas a preguntas frecuentes |

### 👨‍🔧 **Para DevOps/Operations**

| Documento | Nivel | Tiempo | Propósito |
|-----------|-------|--------|----------|
| [GUIA_DEPLOYMENT.md](GUIA_DEPLOYMENT.md) | Senior | 45 min | Deploy a producción, configuración, backups |
| [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md) | Intermedio/Senior | 15 min | Troubleshooting, logs, monitoreo |

### 📖 **Documentación de Referencia**

| Documento | Propósito |
|-----------|----------|
| [ARQUITECTURA_Y_ESTADO_ACTUAL.md](ARQUITECTURA_Y_ESTADO_ACTUAL.md) | Estado del proyecto, patrón arquitectónico |
| [REVISION_TECNICA_2026-04-11.md](REVISION_TECNICA_2026-04-11.md) | Problemas resueltos, recomendaciones |
| [IMPLEMENTACION_SEGURIDAD_Y_ACCESOS.md](IMPLEMENTACION_SEGURIDAD_Y_ACCESOS.md) | Detalles de seguridad implementada |
| [IMPLEMENTACION_RESET_PASSWORD.md](IMPLEMENTACION_RESET_PASSWORD.md) | Flujo de reset de contraseña |

---

## 🚀 Guías de Inicio Rápido

### Quiero crear un nuevo módulo (ej: Sales)

→ **Leer:** [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md)

Esta guía contiene:
- ✅ Paso a paso (11 pasos completos)
- ✅ Ejemplo práctico del módulo `sales`
- ✅ Código copiable
- ✅ Checklist de verificación

**Tiempo:** 30 minutos

---

### Quiero escribir tests para mi módulo

→ **Leer:** [GUIA_TESTING.md](GUIA_TESTING.md)

Esta guía contiene:
- ✅ Frameworks disponibles (unittest, pytest)
- ✅ Patrones de tests para modelos, servicios, vistas
- ✅ Cómo ejecutar y medir cobertura
- ✅ Ejemplos reales de `core/`

**Tiempo:** 30 minutos

---

### Quiero desplegar a producción

→ **Leer:** [GUIA_DEPLOYMENT.md](GUIA_DEPLOYMENT.md)

Esta guía contiene:
- ✅ Variables de entorno por entorno
- ✅ Configuración de PostgreSQL, Nginx, SSL
- ✅ Setup de Gunicorn y systemd
- ✅ Backups automáticos
- ✅ Checklist pre-producción

**Tiempo:** 45 minutos

---

### Necesito referencia rápida de endpoints

→ **Leer:** [REFERENCIA_ENDPOINTS.md](REFERENCIA_ENDPOINTS.md)

Esta referencia contiene:
- ✅ Tabla de todos los endpoints
- ✅ Métodos HTTP, autenticación, permisos
- ✅ Request/Response examples
- ✅ Códigos de estado

**Tiempo:** 10 minutos (búsqueda específica)

---

### Tengo un problema y no sé cómo solucionarlo

→ **Leer:** [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md)

Esta guía contiene:
- ✅ 25+ preguntas frecuentes con respuestas
- ✅ Soluciones paso a paso
- ✅ Comandos ejecutables
- ✅ Troubleshooting por área

**Tiempo:** 10 minutos (búsqueda de tu problema)

---

## 📊 Mapa de Contenidos Detallado

### [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md)

1. Introducción y requisitos
2. Caso práctico: módulo Sales
3. Estructura de carpetas
4. Registrar app en settings
5. **Definir modelos** (heredar BaseModel)
6. **Crear servicios** (lógica de negocio)
7. **Crear formularios** (validaciones)
8. **Crear vistas** (CRUD con mixins)
9. **Configurar URLs**
10. **Crear templates**
11. **Crear migraciones**
12. **Escribir tests**
13. **Registrar en admin**
14. Checklist de implementación
15. Resumen de patrones

### [GUIA_TESTING.md](GUIA_TESTING.md)

1. Frameworks: unittest vs pytest
2. Estructura de tests en el proyecto
3. Patrones en `core/tests.py`
4. Cómo escribir tests (paso a paso)
5. **Tests de modelos**
6. **Tests de servicios**
7. **Tests de formularios**
8. **Tests de vistas**
9. Ejecutar tests (comandos)
10. Cobertura de código
11. Fixtures reutilizables
12. Mocking y patching
13. Tests de integración
14. Troubleshooting

### [GUIA_DEPLOYMENT.md](GUIA_DEPLOYMENT.md)

1. Entornos: dev, staging, producción
2. Variables de entorno por entorno
3. **Base de datos PostgreSQL**
4. **Static files y Nginx**
5. **Servicio WSGI (Gunicorn)**
6. **SSL/HTTPS con Let's Encrypt**
7. **Logging**
8. **Backups automáticos**
9. **Monitoreo y alertas**
10. Checklist pre-producción
11. Troubleshooting deployment
12. Recuperación de desastres

### [REFERENCIA_ENDPOINTS.md](REFERENCIA_ENDPOINTS.md)

1. Endpoints públicos (Home)
2. **Autenticación** (Login, Logout, Password Reset)
3. **Dashboard**
4. **Usuarios** (ABM completo)
5. **Perfil del usuario**
6. **Roles** (ABM completo)
7. **Parámetros del sistema** (ABM completo)
8. Códigos de estado HTTP
9. Permisos por módulo
10. Ejemplo de integración (cURL)
11. Rate limiting

### [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md)

1. **Preguntas de Desarrollo** (6 preguntas)
   - Agregar campos a modelos
   - Crear permisos personalizados
   - Cambiar zona horaria
   - Configurar email
   - Resetear BD
   - Crear usuarios de prueba

2. **Testing y Debugging** (4 preguntas)
   - Errores en tests
   - Debuggear tests
   - Limpiar cache
   - Configuración diferente

3. **Deployment y Producción** (6 preguntas)
   - Checklist pre-deploy
   - Ver logs
   - Rollback de migraciones
   - Redimensionar BD
   - Etc.

4. **Seguridad y Permisos** (4 preguntas)
   - Desbloquear usuario por rate limit
   - Resetear contraseña
   - Cambiar SECRET_KEY
   - Auditoría de cambios

5. **Performance y Cache** (3 preguntas)
   - Parámetros con cache
   - Limpiar cache
   - Medir performance

6. **Errores Comunes** (4 preguntas)
   - ModuleNotFoundError
   - Connection refused
   - CSRF token missing
   - 500 Internal Server Error

---

## 🎓 Orden de Lectura Recomendado

### Primeras 24 horas

1. [README.md](../README.md) - (5 min) - Resumen del proyecto
2. [ARQUITECTURA_Y_ESTADO_ACTUAL.md](ARQUITECTURA_Y_ESTADO_ACTUAL.md) - (15 min) - Entender la arquitectura
3. [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md) - (30 min) - Cómo crear módulos

### Primeros 7 días

4. [GUIA_TESTING.md](GUIA_TESTING.md) - (30 min) - Escribir tests
5. [REFERENCIA_ENDPOINTS.md](REFERENCIA_ENDPOINTS.md) - (15 min) - APIs disponibles
6. [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md) - (según necesidad) - Resolver problemas

### Antes de Deploy

7. [GUIA_DEPLOYMENT.md](GUIA_DEPLOYMENT.md) - (45 min) - Deploy a producción
8. [REVISION_TECNICA_2026-04-11.md](REVISION_TECNICA_2026-04-11.md) - (15 min) - Revisión técnica

### Documentación de Referencia

- [IMPLEMENTACION_SEGURIDAD_Y_ACCESOS.md](IMPLEMENTACION_SEGURIDAD_Y_ACCESOS.md) - Cuando necesites detalles de seguridad
- [IMPLEMENTACION_RESET_PASSWORD.md](IMPLEMENTACION_RESET_PASSWORD.md) - Cuando necesites detalles del reset

---

## 🔍 Búsqueda Rápida

### Por Problema

| Problema | Documento | Sección |
|----------|-----------|---------|
| No sé por dónde empezar | [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md) | Paso 1 |
| Necesito escribir tests | [GUIA_TESTING.md](GUIA_TESTING.md) | "Cómo escribir tests" |
| ¿Qué endpoints hay? | [REFERENCIA_ENDPOINTS.md](REFERENCIA_ENDPOINTS.md) | Tabla de endpoints |
| Usuario bloqueado | [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md) | P15 |
| Quiero desplegar | [GUIA_DEPLOYMENT.md](GUIA_DEPLOYMENT.md) | Paso 1 |
| Migraciones fallaron | [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md) | P13 |
| Tests fallan | [GUIA_TESTING.md](GUIA_TESTING.md) | Troubleshooting |
| 500 error en prod | [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md) | P25 |

### Por Tarea

| Tarea | Documento | Sección |
|-------|-----------|---------|
| Crear nuevo módulo | [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md) | Paso 3-11 |
| Crear modelo | [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md) | Paso 3 |
| Crear servicio | [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md) | Paso 4 |
| Crear vistas | [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md) | Paso 6 |
| Escribir test | [GUIA_TESTING.md](GUIA_TESTING.md) | "Tests de modelos/servicios/vistas" |
| Ejecutar tests | [GUIA_TESTING.md](GUIA_TESTING.md) | "Ejecutar tests" |
| Desplegar | [GUIA_DEPLOYMENT.md](GUIA_DEPLOYMENT.md) | Paso 1-9 |
| Hacer backup | [GUIA_DEPLOYMENT.md](GUIA_DEPLOYMENT.md) | Paso 8 |
| Configurar email | [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md) | P4 |
| Ver logs | [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md) | P12 |

---

## 💡 Tips Útiles

### Para Juniors

1. Lee primero [ARQUITECTURA_Y_ESTADO_ACTUAL.md](ARQUITECTURA_Y_ESTADO_ACTUAL.md) para entender el flujo
2. Sigue [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md) paso a paso para tu primer módulo
3. Copia patrones de `core/` sin variar
4. Consulta [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md) cuando algo no funciona

### Para Seniors

1. Revisa [ARQUITECTURA_Y_ESTADO_ACTUAL.md](ARQUITECTURA_Y_ESTADO_ACTUAL.md) para patrones
2. Customiza según necesidades del proyecto
3. Asegúrate de mantener cobertura de tests >80%
4. Documenta excepciones a patrones

### Para DevOps

1. Lee [GUIA_DEPLOYMENT.md](GUIA_DEPLOYMENT.md) completo antes de primer deploy
2. Usa checklist pre-producción de [GUIA_DEPLOYMENT.md](GUIA_DEPLOYMENT.md) y [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md)
3. Configura backups y monitoreo primero
4. Ten [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md) a mano para troubleshooting

---

## 📝 Convenciones Documentales

- 📋 Tablas: Referencia rápida de opciones
- 🔧 Pasos numerados: Procesos secuenciales
- 💻 Bloques de código: Comandos ejecutables (copy-paste ready)
- ⚠️ Advertencias: Cosas a cuidar
- ✅ Checklists: Verificaciones antes de hacer algo
- **Negrita:** Términos importantes

---

## 🔗 Enlaces Útiles

### Documentación Externa

- [Django 6.0 Official Docs](https://docs.djangoproject.com/en/6.0/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Gunicorn Documentation](https://gunicorn.org/)

### Herramientas Relacionadas

- [Bootstrap 5](https://getbootstrap.com/docs/5.0/) - Framework UI
- [Font Awesome](https://fontawesome.com/) - Iconos
- [pytest Documentation](https://docs.pytest.org/)
- [coverage.py Documentation](https://coverage.readthedocs.io/)

---

## ❓ ¿Qué documento no existe aún?

Si no encuentras lo que buscas:

1. Busca en [FAQ_TROUBLESHOOTING.md](FAQ_TROUBLESHOOTING.md) - Puede que esté como pregunta frecuente
2. Revisa [REVISION_TECNICA_2026-04-11.md](REVISION_TECNICA_2026-04-11.md) - Puede estar documentado allí
3. Abre un issue o pregunta al equipo

---

## 📅 Última Actualización

- **Fecha:** 2026-05-02
- **Documentos:** 6 guías nuevas + 4 documentos anteriores
- **Cobertura:** Desarrollo, Testing, Deployment, API Reference, FAQ

---

## 🙌 Contribuciones

¿Encontraste un error en la documentación? ¿Hay algo que no está claro?

1. Reporta el issue
2. Propón mejoras
3. Ayuda a mantenerla actualizada

**La documentación es un documento vivo. Mantenla actualizada.**
