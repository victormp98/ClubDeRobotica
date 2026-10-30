# Club de Robótica

Aplicación web para gestionar miembros, proyectos, actividades y contenido del club. Backend en Python/Flask con SQLAlchemy, Flask-Login y Flask-Admin; persistencia en MySQL o SQLite según el entorno.

## Módulos

- Autenticación y perfiles de miembros; autorización por rol y estado de aprobación.
- Panel administrativo para miembros, noticias, galerías, horarios, equipos y contenido.
- Gestión de proyectos y tareas con interacción en tiempo real mediante Socket.IO.
- Modelos y migraciones de base de datos con SQLAlchemy y Flask-Migrate.

## Requisitos

- Python 3.11 y dependencias declaradas en `requirements.txt`.
- Variables de configuración en un archivo `.env` local, excluido de Git.
- Motor MySQL para entornos compartidos; SQLite disponible para desarrollo.

## Configuración

`SECRET_KEY` es obligatorio para sesiones, CSRF y tokens de recuperación. Define `DATABASE_URL` para seleccionar la base de datos. Las variables de correo (`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD` y `MAIL_DEFAULT_SENDER`) habilitan notificaciones y recuperación de acceso.

El proceso de creación de la cuenta inicial toma `INITIAL_ADMIN_EMAIL` y `INITIAL_ADMIN_PASSWORD` del entorno. Si faltan, omite la creación de esa cuenta. Usa una contraseña exclusiva para cada instalación.

## Ejecución local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask db upgrade
python run.py
```

Para inicializar el administrador de forma explícita:

```powershell
flask seed-admin
```

## Estructura

- `app/models/`: entidades y relaciones SQLAlchemy.
- `app/views/`: rutas públicas y gestión de sesiones.
- `app/admin_views.py`: vistas y permisos de Flask-Admin.
- `app/templates/`: páginas Jinja2 y plantillas de correo.
- `migrations/`: esquema y migraciones Alembic.

## Recuperación de cuentas

La recuperación individual utiliza un token firmado con expiración y la dirección de correo del usuario. Configura SMTP antes de habilitar este flujo. No asignes una contraseña compartida a un grupo de cuentas.

## Datos locales

El archivo `.env`, las bases SQLite y los artefactos generados están excluidos mediante `.gitignore`. No almacenes credenciales de usuarios, tokens ni volcados de bases de datos en el repositorio público.
