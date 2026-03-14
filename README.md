# Club de Robótica

Este es el repositorio oficial del Club de Robótica, una aplicación web desarrollada con Flask, SQLAlchemy y MySQL.

## Arquitectura de Base de Datos Base

Para este proyecto utilizamos SQLAlchemy ORM.

### Esquema de Modelos

#### `User` (Usuarios)
* **id**: Clave primaria
* **email**: Correo único
* **password_hash**: Contraseña encriptada
* **nombre**: Nombre del usuario
* **carrera**: Carrera del estudiante
* **area_interes**: Intereses dentro de la robótica
* **rol**: admin, miembro, visitante
* **aprobado**: Confirmación del usuario
* **fecha_registro**: Timestamp UTC
* **activo**: Borrado lógico (bool)
* *Relación*: Un usuario puede tener muchas `noticias`.

#### `Noticia` (Noticias del Club)
* **id**: Clave primaria
* **titulo**: Título 
* **contenido**: Cuerpo entero (Text)
* **fecha_publicacion**: Timestamp UTC
* **autor_id**: Foreign Key hacia `User`
* **imagen**: URL o path de la imagen
* **activo**: Borrado lógico (bool)

#### `Horario` (Horarios del lugar o actividades)
* **id**: Clave primaria
* **dia_semana**: Ej: Lunes, Martes
* **hora_inicio**: Hora de inicio (Time)
* **hora_fin**: Hora de cierre (Time)
* **descripcion**: Notas extra
* **activo**: Borrado lógico (bool)

#### `Album` (Álbumes de la Galería)
* **id**: Clave primaria
* **nombre**: Nombre del evento
* **descripcion**: Sinopsis
* **fecha_creacion**: Timestamp UTC
* **activo**: Borrado lógico (bool)
* *Relación*: Un álbum contiene múltiples `fotos`. (Cascade delete configurado)

#### `Foto` (Fotos individuales)
* **id**: Clave primaria
* **titulo**: Titulo de la foto
* **imagen_path**: URL o locación local
* **album_id**: Foreign Key hacia `Album`
* **fecha_subida**: Timestamp UTC 
* **activo**: Borrado lógico (bool)
