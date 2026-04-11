# Revisión Técnica del Proyecto ERP

Fecha: 2026-04-11

## 1) Alcance revisado
Se revisaron configuración global, app `core`, estructura de tests, documentación existente y estado de las apps de dominio no implementadas.

## 2) Hallazgos confirmados

### Crítico
1. La suite completa no ejecutaba por colisión entre archivos `tests.py` y paquetes `tests/` en varias apps scaffolded.
   - Impacto: `python manage.py test` fallaba antes de descubrir casos reales.
   - Estado: corregido eliminando los `tests.py` vacíos de las apps que ya usan `tests/`.

### Alto
2. `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` estaban acoplados a valores fijos en configuración.
   - Impacto: mala práctica de seguridad y despliegue poco portable.
   - Estado: ajustado para leer desde entorno con `.env.example` de referencia.

3. El `README.md` describía módulos de negocio como si estuvieran implementados cuando en realidad solo existían como scaffold.
   - Impacto: documentación engañosa para desarrollo, QA o despliegue.
   - Estado: corregido documentando el estado real del repositorio.

### Medio
4. Existe una diferencia fuerte entre la arquitectura real (`core`) y la arquitectura declarada para el resto de las apps.
   - Impacto: riesgo de crecimiento inconsistente cuando se implementen nuevos dominios.
   - Estado: documentado en `ARQUITECTURA_Y_ESTADO_ACTUAL.md`.

5. La cobertura de tests está concentrada casi por completo en `core`.
   - Impacto: el crecimiento de módulos de negocio puede ocurrir sin base mínima de regresión.
   - Estado: documentado.

### Bajo
6. Hay vistas que capturan `Exception` genérica y muestran mensajes al usuario.
   - Impacto: menor granularidad para manejo de errores de negocio y depuración.
   - Archivos relevantes: `core/views/user_views.py`, `core/views/role_views.py`.

7. Hay comentarios heredados del scaffold de Django y textos de documentación generados por defecto que ya no representan el estado real.
   - Impacto: ruido documental y mantenimiento más difícil.

## 3) Fortalezas observadas

- separación razonable entre modelos, formularios, servicios y vistas en `core`
- uso de mixins para control de acceso y auditoría
- implementación funcional de login, rate limit, cambio de contraseña y reset de contraseña
- suite de tests útil en `core` para seguridad y permisos

## 4) Recomendaciones priorizadas

1. Mantener el patrón `tests/` por app y evitar volver a introducir `tests.py` cuando ya exista un paquete de pruebas.
2. Extender documentación por módulo a medida que se implementen `masters`, `purchases`, `sales`, `inventory`, `accounting` y `reports`.
3. Reducir capturas genéricas de excepciones en vistas y mover errores esperables a validaciones o excepciones de dominio.
4. Agregar suites mínimas por app al comenzar cada dominio funcional nuevo.
5. Revisar periódicamente que README y documentación reflejen estado real y no roadmap implícito.