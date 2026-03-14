# Documentación Técnica – Club de Robótica UNACH

> **Versión:** 1.0-dev · **Fecha:** Marzo 2026 · **Autor:** Equipo Técnico

---

## 1. Descripción General

El sitio web del **Club de Robótica de la UNACH** es una aplicación web full-stack desarrollada en Python/Flask con una base de datos MySQL. Provee una plataforma institucional que incluye:

- Portal público informativo (noticias, galería, horarios, páginas de contenido).
- Sistema de registro y autenticación de miembros con roles.
- Panel administrativo protegido (Flask-Admin) para gestión de contenido.

---

## 2. Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Backend** | Python 3.11, Flask 3.x |
| **ORM / BD** | SQLAlchemy 2.x + Flask-Migrate, MySQL (producción) / SQLite (dev) |
| **Autenticación** | Flask-Login, Werkzeug Security (PBKDF2) |
| **Formularios** | Flask-WTF, WTForms |
| **Admin Panel** | Flask-Admin |
| **Email** | Flask-Mail (SMTP / async thread) |
| **Imágenes** | Pillow (resize + compress), Flask-Admin ImageUploadField |
| **Frontend** | Tailwind CSS (CDN), AOS.js, GLightbox |
| **Deployment** | Passenger WSGI (Shared Hosting / cPanel) |

---

## 3. Estructura del Proyecto

```
ClubDeRobotica/
├── Passenger_WSGI.py        # Punto de entrada para producción (cPanel)
├── seed_pages.py            # Script seeder para páginas iniciales
├── app/
│   ├── __init__.py          # App Factory, registro de extensiones y blueprints
│   ├── extensions.py        # Instancias globales: db, migrate, mail, login_manager
│   ├── config.py            # Configuraciones por entorno
│   ├── forms.py             # Clases WTForms: LoginForm, RegistrationForm, NoticiaForm
│   ├── admin_views.py       # Vistas Flask-Admin: UserAdmin, NoticiaAdmin, PageAdmin…
│   ├── models/
│   │   ├── user.py          # Modelo User (UserMixin, roles, hash)
│   │   ├── noticia.py       # Modelo Noticia
│   │   ├── horario.py       # Modelo Horario
│   │   ├── album.py         # Modelo Album (galería)
│   │   ├── foto.py          # Modelo Foto
│   │   └── page.py          # Modelo Page (CMS páginas estáticas)
│   ├── views/
│   │   └── main.py          # Blueprint principal: todas las rutas públicas
│   ├── static/
│   │   └── uploads/
│   │       ├── noticias/    # Imágenes de noticias optimizadas
│   │       └── galeria/     # Fotos de galería (auto-comprimidas con Pillow)
│   └── templates/
│       ├── base.html        # Layout base con Navbar/Footer
│       ├── index.html       # Inicio
│       ├── about.html       # Sobre el Club (CMS-ready)
│       ├── login.html       # Formulario de inicio de sesión
│       ├── registro.html    # Formulario de registro de miembros
│       ├── horarios.html    # Vista pública de horarios dinámicos
│       ├── noticias/        # index.html + detalle.html
│       ├── galeria/         # index.html (álbumes) + album.html (fotos)
│       └── miembros/
│           └── index.html   # Dashboard exclusivo para miembros aprobados
├── migrations/              # Archivos de migración Alembic
└── venv/                    # Entorno virtual Python
```

---

## 4. Modelos de Base de Datos

### 4.1 `User` — Usuarios

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | Clave primaria |
| `email` | String(120) UNIQUE | Correo (identidad de acceso) |
| `password_hash` | String(256) | Contraseña cifrada PBKDF2 |
| `nombre` | String(100) | Nombre completo |
| `carrera` | String(100) | Carrera universitaria |
| `area_interes` | String(100) | Área de interés en robótica |
| `rol` | String(20) | `'admin'`, `'miembro'`, `'visitante'` |
| `aprobado` | Boolean | Aprobado por el administrador |
| `activo` | Boolean | Soft-delete flag |
| `fecha_registro` | DateTime | Timestamp de registro (UTC) |

### 4.2 `Noticia` — Noticias

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | — |
| `titulo` | String(200) | Título de la noticia |
| `contenido` | Text | Cuerpo HTML |
| `imagen` | String | Nombre de archivo en `/uploads/noticias/` |
| `autor_id` | FK → User | Autor de la noticia |
| `fecha_publicacion` | DateTime | Fecha publicación (UTC) |
| `activo` | Boolean | Visibilidad pública |

### 4.3 `Horario` — Horarios

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | — |
| `dia_semana` | String | `'Lunes'`…`'Domingo'` |
| `hora_inicio` | Time | Hora de inicio |
| `hora_fin` | Time | Hora de fin |
| `descripcion` | String | Nivel / descripción del taller |
| `activo` | Boolean | Visibilidad pública |

### 4.4 `Album` — Álbumes de Galería

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | — |
| `nombre` | String(150) | Nombre del evento |
| `descripcion` | Text | Descripción del álbum |
| `fecha_creacion` | DateTime | Timestamp (UTC) |
| `activo` | Boolean | Visibilidad pública |

### 4.5 `Foto` — Fotografías

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | — |
| `titulo` | String(150) | Título / caption |
| `imagen_path` | String | Nombre del archivo en `/uploads/galeria/` |
| `album_id` | FK → Album | Álbum contenedor |
| `fecha_subida` | DateTime | Timestamp (UTC) |
| `activo` | Boolean | Visibilidad pública |

### 4.6 `Page` — Páginas de Contenido CMS

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer PK | — |
| `slug` | String(100) UNIQUE | Identificador URL (`about`, `contact`, `terminos`) |
| `titulo` | String(200) | Título de la página |
| `contenido` | Text | Cuerpo HTML editable desde el Admin |
| `ultima_modificacion` | DateTime | Auto-updated timestamp |

---

## 5. Módulos y Funcionalidades

### 5.1 Autenticación y Roles (Flask-Login)

- **Rutas**: `/login`, `/logout`, `/registro`
- **Roles**: `admin` (acceso total), `miembro` (panel de miembros), `visitante` (solo público).
- **Seguridad**: Contraseñas con `werkzeug.security.generate_password_hash` (PBKDF2).
- **Decorador custom**: `@miembro_required` — verifica sesión activa **y** `aprobado=True`.
- **Admin Reset**: Acción de lote en `UserAdmin` para resetear contraseña a `"robotica2026"`.

### 5.2 Panel Administrativo (Flask-Admin en `/admin`)

Protegido por `is_accessible()` que exige `current_user.rol == 'admin'`.

| Vista Admin | Modelo | Funcionalidades clave |
|-------------|--------|-----------------------|
| `UserAdmin` | User | Aprobación masiva, reset contraseña, soft-delete, CSV export |
| `NoticiaAdmin` | Noticia | Upload imagen (Pillow resize 1920x1080), publicación |
| `AlbumAdmin` | Album | Gestión de álbumes de galería |
| `FotoAdmin` | Foto | Upload foto (Pillow resize 1200x1200), miniatura preview |
| `HorarioAdmin` | Horario | SelectField días semana, activar/desactivar |
| `PageAdmin` | Page | Editor HTML inline por slug, slug de solo-lectura |

### 5.3 Galería Pública (GLightbox)

- **Rutas**: `/galeria` (lista álbumes), `/galeria/<id>` (fotos del álbum).
- **Lightbox**: GLightbox vía CDN con soporte táctil, loop y zoom.
- **Imágenes**: Auto-comprimidas con Pillow al subir (máx 1200px).

### 5.4 Noticias

- **Rutas**: `/noticias` (paginado, 9 por página), `/noticias/<id>` (detalle).
- **Inicio**: Últimas 3 noticias activas en `index.html`.

### 5.5 Horarios Dinámicos

- **Ruta**: `/horarios`
- Solo muestra horarios con `activo=True`.
- Ordenados por día (Lunes→Domingo) mediante diccionario numérico en Python.
- Incluye nota: *"Los horarios mostrados están sujetos a cambios."*

### 5.6 CMS Páginas Estáticas

- **Modelo**: `Page` con `slug` único.
- **Slugs iniciales**: `about`, `contact`, `terminos` (sembrados con `seed_pages.py`).
- **Admin**: `PageAdmin` permite editar el HTML de cada página.
- **Frontend**: Content renderizado con `{{ page.contenido | safe }}` en Jinja2.

---

## 6. Instalación y Configuración Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/victormp98/ClubDeRobotica.git
cd ClubDeRobotica

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (.env o config.py)
# DATABASE_URL, SECRET_KEY, MAIL_* settings

# 5. Inicializar base de datos
flask db upgrade

# 6. Sembrar páginas iniciales
python seed_pages.py

# 7. Correr servidor de desarrollo
flask run
```

---

## 7. Variables de Entorno Requeridas

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave secreta Flask (CSRF, sesiones) |
| `DATABASE_URL` | URI de conexión MySQL/SQLite |
| `MAIL_SERVER` | Servidor SMTP |
| `MAIL_PORT` | Puerto SMTP (ej. 587) |
| `MAIL_USERNAME` | Usuario SMTP |
| `MAIL_PASSWORD` | Contraseña SMTP |
| `MAIL_DEFAULT_SENDER` | Remitente por defecto |

---

## 8. Deployment en Producción (cPanel / Shared Hosting)

El punto de entrada para Passenger WSGI es `Passenger_WSGI.py`:

```python
from app import create_app
application = create_app()
```

Pasos básicos:
1. Subir archivos vía FTP/Git.
2. Instalar dependencias en el venv del hosting.
3. Configurar la aplicación Python en cPanel apuntando a `Passenger_WSGI.py`.
4. Ejecutar `flask db upgrade` vía SSH.
5. Ejecutar `python seed_pages.py` para sembrar contenido inicial.

---

## 9. Pendientes / Backlog

- [ ] Editor WYSIWYG (TinyMCE/Quill) para `PageAdmin` y `NoticiaAdmin`.
- [ ] Gestión de perfil de miembro (cambio de contraseña propio).
- [ ] Sistema de notificaciones push o email al publicar noticias.
- [ ] Integración de resultados WRO y torneos.

---

*Documentación generada a partir del estado actual del repositorio en Marzo 2026.*
