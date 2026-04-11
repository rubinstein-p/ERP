# Implementación del Reset de Contraseña en ERP Django

## Descripción General
El sistema de reset de contraseña permite a los usuarios recuperar el acceso a sus cuentas cuando olvidan su contraseña. Utiliza las vistas estándar de Django `django.contrib.auth.views` personalizadas para el proyecto ERP.

## Flujo de Funcionamiento

### 1. Enlace de Inicio del Reset
- **Ubicación del enlace**: `core/templates/core/login.html` (línea 67)
- **Texto del enlace**: "¿Olvidaste tu contraseña? Restablécela aquí"
- **URL destino**: `{% url 'core:password_reset' %}` que apunta a `/password-reset/`

### 2. Formulario de Solicitud de Reset
- **Vista**: `UserPasswordResetView` en `core/views/user_views.py` (líneas 78-83)
- **Template**: `core/templates/core/password_reset_form.html`
- **URL**: `core/urls.py` - `path('password-reset/', UserPasswordResetView.as_view(), name='password_reset')`
- **Funcionalidad**: El usuario ingresa su email. Django valida si existe un usuario con ese email y envía un email con el enlace de reset.

### 3. Confirmación de Envío de Email
- **Vista**: `UserPasswordResetDoneView` en `core/views/user_views.py` (línea 86)
- **Template**: `core/templates/core/password_reset_done.html`
- **URL**: `core/urls.py` - `path('password-reset/done/', UserPasswordResetDoneView.as_view(), name='password_reset_done')`
- **Funcionalidad**: Muestra un mensaje confirmando que se envió el email (si el email existe en el sistema).

### 4. Email de Reset
- **Template del email**: `core/templates/core/password_reset_email.txt`
- **Template del asunto**: `core/templates/core/password_reset_subject.txt`
- **Contenido**: Incluye un enlace con tokens únicos (`uidb64` y `token`) para verificar la autenticidad de la solicitud.
- **Enlace generado**: `{{ protocol }}://{{ domain }}{% url 'core:password_reset_confirm' uidb64=uid token=token %}`
- **Asunto**: "Restablecimiento de contraseña - ERP"

### 5. Formulario de Nueva Contraseña
- **Vista**: `UserPasswordResetConfirmView` en `core/views/user_views.py` (líneas 89-92)
- **Template**: `core/templates/core/password_reset_confirm.html`
- **URL**: `core/urls.py` - `path('password-reset/confirm/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm')`
- **Funcionalidad**: Valida el token y permite al usuario ingresar una nueva contraseña. Incluye validación de coincidencia entre los dos campos de contraseña.

### 6. Confirmación de Reset Completado
- **Vista**: `UserPasswordResetCompleteView` en `core/views/user_views.py` (línea 95)
- **Template**: `core/templates/core/password_reset_complete.html`
- **URL**: `core/urls.py` - `path('password-reset/complete/', UserPasswordResetCompleteView.as_view(), name='password_reset_complete')`
- **Funcionalidad**: Confirma que la contraseña se cambió exitosamente y redirige al login.

## Archivos Involucrados

### Vistas
- `core/views/user_views.py`: Contiene las clases `UserPasswordResetView`, `UserPasswordResetDoneView`, `UserPasswordResetConfirmView`, `UserPasswordResetCompleteView`

### URLs
- `core/urls.py`: Define las rutas para cada paso del proceso de reset

### Templates
- `core/templates/core/login.html`: Contiene el enlace inicial "¿Olvidaste tu contraseña?"
- `core/templates/core/password_reset_form.html`: Formulario para ingresar email
- `core/templates/core/password_reset_done.html`: Página de confirmación de envío de email
- `core/templates/core/password_reset_email.txt`: Contenido del email enviado
- `core/templates/core/password_reset_subject.txt`: Asunto del email
- `core/templates/core/password_reset_confirm.html`: Formulario para nueva contraseña
- `core/templates/core/password_reset_complete.html`: Confirmación final

### Configuración
- Utiliza la configuración estándar de Django para envío de emails (ver `erp/settings.py` para EMAIL_BACKEND, etc.)

## Seguridad
- Utiliza tokens únicos generados por Django que incluyen el ID del usuario codificado en base64 (`uidb64`) y un token de verificación
- Los tokens tienen expiración automática
- No revela si un email existe o no en el sistema (para evitar enumeración de usuarios)
- Requiere que el usuario confirme la nueva contraseña dos veces

## Notas Adicionales
- El sistema hereda toda la funcionalidad de seguridad de `django.contrib.auth`
- Los templates están diseñados con Bootstrap para consistencia visual
- Incluye íconos de FontAwesome para mejor UX</content>
<parameter name="filePath">c:\Personales\Django\ERP\documentacion\IMPLEMENTACION_RESET_PASSWORD.md