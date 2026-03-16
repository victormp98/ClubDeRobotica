import os
from flask import current_app

def delete_image_files(filename, subfolder):
    """
    Elimina físicamente el archivo de imagen y su miniatura del servidor.
    :param filename: Nombre del archivo guardado en la BD.
    :param subfolder: Subcarpeta dentro de static/uploads (ej: 'noticias', 'galeria').
    """
    if not filename:
        return

    # Construir ruta base
    # Usamos path absoluto basado en el root de la app
    base_path = os.path.join(current_app.root_path, 'static', 'uploads', subfolder)
    
    # Archivo principal
    main_file = os.path.join(base_path, filename)
    
    # Archivo miniatura (Flask-Admin suele usar _thumb antes de la extensión)
    # Ejemplo: uuid.png -> uuid_thumb.png
    name, ext = os.path.splitext(filename)
    thumb_file = os.path.join(base_path, f"{name}_thumb{ext}")

    # Intentar borrar archivos
    for file_path in [main_file, thumb_file]:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[CLEANUP] Archivo eliminado: {file_path}")
        except Exception as e:
            print(f"[CLEANUP_ERROR] No se pudo eliminar {file_path}: {str(e)}")

def register_cleanup_listeners(db):
    """
    Registra los listeners de SQLAlchemy para automatizar la limpieza.
    """
    from sqlalchemy import event
    from app.models.noticia import Noticia
    from app.models.foto import Foto
    from app.models.proyecto import Proyecto
    from app.models.miembro_equipo import MiembroEquipo
    from app.models.configuracion import Configuracion

    # --- NOTICIAS ---
    @event.listens_for(Noticia, 'after_delete')
    def cleanup_noticia_delete(mapper, connection, target):
        if target.imagen:
            delete_image_files(target.imagen, 'noticias')

    @event.listens_for(Noticia, 'after_update')
    def cleanup_noticia_update(mapper, connection, target):
        state = db.inspect(target)
        history = state.get_history('imagen', True)
        if history.has_changes() and history.deleted:
            # Borrar la imagen anterior
            old_image = history.deleted[0]
            if old_image:
                delete_image_files(old_image, 'noticias')

    # --- GALERIA (FOTOS) ---
    @event.listens_for(Foto, 'after_delete')
    def cleanup_foto_delete(mapper, connection, target):
        if target.imagen_path:
            delete_image_files(target.imagen_path, 'galeria')

    @event.listens_for(Foto, 'after_update')
    def cleanup_foto_update(mapper, connection, target):
        state = db.inspect(target)
        history = state.get_history('imagen_path', True)
        if history.has_changes() and history.deleted:
            old_image = history.deleted[0]
            if old_image:
                delete_image_files(old_image, 'galeria')

    # --- PROYECTOS ---
    @event.listens_for(Proyecto, 'after_delete')
    def cleanup_proyecto_delete(mapper, connection, target):
        if target.imagen_path:
            delete_image_files(target.imagen_path, 'proyectos')

    @event.listens_for(Proyecto, 'after_update')
    def cleanup_proyecto_update(mapper, connection, target):
        state = db.inspect(target)
        history = state.get_history('imagen_path', True)
        if history.has_changes() and history.deleted:
            old_image = history.deleted[0]
            if old_image:
                delete_image_files(old_image, 'proyectos')

    # --- EQUIPO ---
    @event.listens_for(MiembroEquipo, 'after_delete')
    def cleanup_equipo_delete(mapper, connection, target):
        if target.foto_path:
            delete_image_files(target.foto_path, 'equipo')

    @event.listens_for(MiembroEquipo, 'after_update')
    def cleanup_equipo_update(mapper, connection, target):
        state = db.inspect(target)
        history = state.get_history('foto_path', True)
        if history.has_changes() and history.deleted:
            old_image = history.deleted[0]
            if old_image:
                delete_image_files(old_image, 'equipo')

    # --- CONFIGURACION ---
    @event.listens_for(Configuracion, 'after_update')
    def cleanup_config_update(mapper, connection, target):
        # En configuración, solo nos interesa si la llave termina en imagen o es una llave de imagen conocida
        # o si el administrador subió una imagen vía ConfiguracionAdmin
        state = db.inspect(target)
        history = state.get_history('valor', True)
        if history.has_changes() and history.deleted:
            old_val = history.deleted[0]
            # Solo intentamos borrar si el valor parece un nombre de archivo (tiene extensión de imagen)
            if old_val and any(old_val.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                delete_image_files(old_val, 'config')
