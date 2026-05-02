# Guía de Deployment: Configuración para Producción

Fecha: 2026-05-02

## Introducción

Esta guía cubre cómo preparar, configurar y desplegar el ERP Django en un ambiente de producción. Incluye checklist pre-producción, configuración segura, base de datos, web server y backup.

**Audiencia:** DevOps, SysAdmins, Developers en roles de deployment.

---

## Entornos

El ERP soporta 3 entornos: **Desarrollo**, **Staging**, **Producción**.

| Aspecto | Desarrollo | Staging | Producción |
|--------|-----------|---------|-----------|
| `DEBUG` | `True` | `False` | `False` |
| `SECRET_KEY` | Local | Generada | **Fuerte y secreta** |
| `ALLOWED_HOSTS` | `localhost` | Dominio staging | Dominio real |
| `DATABASE_URL` | SQLite local | PostgreSQL | **PostgreSQL persistente** |
| `EMAIL_BACKEND` | Console | SMTP real | SMTP real |
| `STATIC_FILES` | Auto-servidas | Colectadas | Nginx |
| `HTTPS` | No | Sí | **Sí (SSL)** |
| `Backups` | Manual | Diario | **Diario** |

---

## Paso 1: Variables de Entorno para Producción

Crea el archivo `.env` en producción basado en `.env.example`:

```bash
# .env (PRODUCCIÓN)

# ========== SEGURIDAD ==========
SECRET_KEY=tu-clave-secreta-super-fuerte-aqui-123abc456
DEBUG=False
ALLOWED_HOSTS=erp.tuempresa.com,www.erp.tuempresa.com
CSRF_TRUSTED_ORIGINS=https://erp.tuempresa.com,https://www.erp.tuempresa.com

# ========== BASE DE DATOS ==========
# PostgreSQL en servidor remoto
DATABASE_URL=postgresql://user:password@db.tuempresa.com:5432/erp_production

# ========== IDIOMA Y ZONA HORARIA ==========
LANGUAGE_CODE=es-ar
TIME_ZONE=America/Argentina/Tucuman
USE_TZ=True

# ========== EMAIL (SMTP REAL) ==========
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-app-gmail
DEFAULT_FROM_EMAIL=ERP <noreply@tuempresa.com>

# ========== SEGURIDAD DE LOGIN ==========
LOGIN_MAX_ATTEMPTS=5
LOGIN_LOCKOUT_SECONDS=900
PASSWORD_RESET_TIMEOUT=3600

# ========== DJANGO SETTINGS ==========
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# ========== LOGGING ==========
LOG_LEVEL=INFO
LOG_DIR=/var/log/erp/
```

### Generar SECRET_KEY segura

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Paso 2: Configurar Base de Datos (PostgreSQL)

### Crear base de datos en PostgreSQL

```bash
# En servidor PostgreSQL
sudo -u postgres psql

CREATE DATABASE erp_production;
CREATE USER erp_user WITH PASSWORD 'tu-password-segura';
ALTER ROLE erp_user SET client_encoding TO 'utf8';
ALTER ROLE erp_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE erp_user SET default_transaction_deferrable TO on;
ALTER ROLE erp_user SET timezone TO 'America/Argentina/Tucuman';
GRANT ALL PRIVILEGES ON DATABASE erp_production TO erp_user;
\q
```

### Verificar conexión

```bash
python manage.py dbshell
# Si se conecta exitosamente, la configuración es correcta
```

---

## Paso 3: Configurar Static Files

### Recolectar static files

```bash
python manage.py collectstatic --noinput
```

Esto copia archivos a la carpeta configurada en `STATIC_ROOT` (por defecto `/var/www/erp/staticfiles/`).

### Servir static files con Nginx

En tu configuración nginx:

```nginx
server {
    listen 80;
    server_name erp.tuempresa.com;
    
    # Redirigir HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name erp.tuempresa.com www.erp.tuempresa.com;
    
    # ========== SSL ==========
    ssl_certificate /etc/letsencrypt/live/erp.tuempresa.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.tuempresa.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ========== STATIC FILES ==========
    location /static/ {
        alias /var/www/erp/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/erp/media/;
        expires 7d;
    }
    
    # ========== PROXY DJANGO ==========
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    # ========== SECURITY HEADERS ==========
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

---

## Paso 4: Servicio WSGI (Gunicorn + Supervisor)

### Instalar Gunicorn

```bash
pip install gunicorn
```

### Script de inicio Gunicorn

Crea `/etc/systemd/system/erp-gunicorn.service`:

```ini
[Unit]
Description=ERP Gunicorn Service
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/erp
ExecStart=/var/www/erp/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/erp/gunicorn-access.log \
    --error-logfile /var/log/erp/gunicorn-error.log \
    erp.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Habilitar y arrancar servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable erp-gunicorn
sudo systemctl start erp-gunicorn
sudo systemctl status erp-gunicorn
```

### Ver logs

```bash
sudo tail -f /var/log/erp/gunicorn-error.log
sudo tail -f /var/log/erp/gunicorn-access.log
```

---

## Paso 5: Migraciones en Producción

### Ejecutar migraciones

```bash
python manage.py migrate
```

### Crear superusuario

```bash
python manage.py createsuperuser
```

### Inicializar roles

```bash
python manage.py create_default_roles --extended
```

---

## Paso 6: SSL/HTTPS con Let's Encrypt

### Instalar Certbot

```bash
sudo apt-get install certbot python3-certbot-nginx
```

### Obtener certificado

```bash
sudo certbot certonly --nginx -d erp.tuempresa.com -d www.erp.tuempresa.com
```

### Auto-renovar certificados

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Verificar
sudo systemctl status certbot.timer
```

---

## Paso 7: Configuración de Logging

Crea `/var/log/erp/` directorio:

```bash
sudo mkdir -p /var/log/erp
sudo chown www-data:www-data /var/log/erp
sudo chmod 755 /var/log/erp
```

### Django logging configuration

Añade a `erp/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': env('LOG_DIR', default='/var/log/erp/') + 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': env('LOG_DIR', default='/var/log/erp/') + 'audit.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'core.services.audit_service': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## Paso 8: Backups Automáticos

### Script de backup de BD

Crea `/usr/local/bin/backup-erp-db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/erp"
DB_USER="erp_user"
DB_NAME="erp_production"
DB_HOST="localhost"
RETENTION_DAYS=30

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Generar backup
BACKUP_FILE="$BACKUP_DIR/erp_db_$(date +%Y%m%d_%H%M%S).sql"
pg_dump -U $DB_USER -h $DB_HOST $DB_NAME | gzip > $BACKUP_FILE.gz

echo "Backup creado: $BACKUP_FILE.gz"

# Eliminar backups antiguos
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete

# Opcional: Enviar a S3
# aws s3 cp $BACKUP_FILE.gz s3://tu-bucket-erp/backups/

echo "Backups antiguos eliminados"
```

### Hacer ejecutable

```bash
sudo chmod +x /usr/local/bin/backup-erp-db.sh
```

### Agregar a crontab (diario a las 2 AM)

```bash
sudo crontab -e

# Agregar:
0 2 * * * /usr/local/bin/backup-erp-db.sh >> /var/log/erp/backup.log 2>&1
```

### Verificar backups

```bash
ls -lh /var/backups/erp/
```

---

## Paso 9: Monitoreo y Alertas

### Monitorear estado de servicios

```bash
sudo systemctl status erp-gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql
```

### Ver recursos del sistema

```bash
# Uso de memoria/CPU
top -b -n 1 | head -20

# Espacio en disco
df -h

# Conexiones a BD
sudo -u postgres psql -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

### Script de health check

Crea `/usr/local/bin/health-check-erp.sh`:

```bash
#!/bin/bash

# Verifica que ERP está respondiendo
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://erp.tuempresa.com/dashboard/)

if [ $STATUS -eq 200 ]; then
    echo "✅ ERP está OK"
else
    echo "❌ ERP está caído (HTTP $STATUS)"
    # Enviar alerta
    # mail -s "ALERTA: ERP caído" admin@tuempresa.com
    systemctl restart erp-gunicorn
fi
```

### Agregar a crontab (cada 5 minutos)

```bash
sudo crontab -e

# Agregar:
*/5 * * * * /usr/local/bin/health-check-erp.sh
```

---

## Checklist Pre-Producción

Antes de hacer deploy:

- [ ] `.env` configurado con valores de producción
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` fuerte y única
- [ ] `ALLOWED_HOSTS` correcto
- [ ] Base de datos PostgreSQL creada y conectada
- [ ] `python manage.py check` sin errores
- [ ] `python manage.py collectstatic` completado
- [ ] Tests ejecutados: `python manage.py test`
- [ ] Migraciones aplicadas: `python manage.py migrate`
- [ ] Superusuario creado
- [ ] Roles inicializados: `python manage.py create_default_roles --extended`
- [ ] SSL/HTTPS configurado
- [ ] Nginx configurado y testado
- [ ] Gunicorn arrancando correctamente
- [ ] Logs configurados
- [ ] Backups configurados
- [ ] Health check configurado
- [ ] Documentar credenciales en gestor seguro (1Password, LastPass, etc.)
- [ ] Comunicar cambios a equipo

---

## Troubleshooting Deployment

### Error: "502 Bad Gateway"

**Causa:** Gunicorn no está respondiendo.

**Solución:**

```bash
# Verificar que Gunicorn está corriendo
sudo systemctl status erp-gunicorn

# Ver logs
sudo tail -f /var/log/erp/gunicorn-error.log

# Reiniciar
sudo systemctl restart erp-gunicorn
```

### Error: "ModuleNotFoundError: No module named 'django'"

**Causa:** Entorno virtual no activado.

**Solución:**

```bash
# Verificar que el venv existe
ls /var/www/erp/venv/

# Reinstalar dependencias
/var/www/erp/venv/bin/pip install -r /var/www/erp/requirements.txt
```

### Error: "could not connect to server: Connection refused"

**Causa:** PostgreSQL no está accesible.

**Solución:**

```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# Verificar credenciales de BD
psql -U erp_user -h localhost -d erp_production
```

### Error: "CSRF token missing"

**Causa:** `CSRF_TRUSTED_ORIGINS` no configurado.

**Solución:**

Verificar `.env`:

```bash
CSRF_TRUSTED_ORIGINS=https://erp.tuempresa.com,https://www.erp.tuempresa.com
```

---

## Recuperación de Desastres

### Restaurar backup de BD

```bash
# Listar backups
ls -lh /var/backups/erp/

# Restaurar
gunzip < /var/backups/erp/erp_db_20260501_020000.sql.gz | psql -U erp_user -h localhost erp_production
```

### Rollback de migraciones

```bash
# Ver migraciones aplicadas
python manage.py showmigrations

# Revertir última migración
python manage.py migrate sales 0001

# Después replicar en código
```

### Reinicio completo del servicio

```bash
sudo systemctl stop erp-gunicorn
sudo systemctl stop nginx
# Verificar, hacer cambios necesarios...
sudo systemctl start nginx
sudo systemctl start erp-gunicorn
```

---

## Recursos Útiles

- [Django Deployment Documentation](https://docs.djangoproject.com/en/6.0/howto/deployment/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Nginx Documentation](https://nginx.org/)
- [Let's Encrypt](https://letsencrypt.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## Próximos Pasos

1. Configurar CI/CD (GitHub Actions para auto-deploy)
2. Agregar CDN para static files
3. Configurar alertas (Sentry, NewRelic)
4. Configurar autoscaling si aplica
5. Documentar runbooks para operaciones
