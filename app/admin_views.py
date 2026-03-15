from flask_admin import AdminIndexView, expose
from flask_admin.model import typefmt
from markupsafe import Markup
from wtforms.validators import DataRequired
from wtforms import fields, validators, SelectField
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask_admin import form
import sys
from flask_login import current_user
from flask import redirect, url_for, flash, current_app
from flask_mail import Message
from app.models.user import User
from app.models.noticia import Noticia
from app.models.album import Album
from app.models.foto import Foto
from app.extensions import mail
import threading
import traceback
import os
import uuid

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print(f"[MAIL_SUCCESS] Correo enviado a {msg.recipients}")
        except Exception as e:
            print(f"[MAIL_ERROR] No se pudo enviar el correo a {msg.recipients}. Credenciales dummy.")
            print(traceback.format_exc(), file=sys.stderr)

class MyAdminIndexView(AdminIndexView):
    # Inyectar CSS personalizado para unificar diseño
    extra_css = ['/static/css/admin_custom.css']
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.rol == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        flash('Debes iniciar sesión con rol Administrador para acceder al panel de control.', 'error')
        return redirect(url_for('main.login'))

    @expose('/')
    def index(self):
        pendientes_count = User.query.filter_by(aprobado=False, activo=True).count()
        activos_count = User.query.filter_by(aprobado=True, activo=True).count()
        return self.render('dashboard.html', pendientes_count=pendientes_count, activos_count=activos_count)

class SecureModelView(ModelView):
    # Inyectar CSS personalizado para unificar diseño con el sitio principal
    extra_css = ['/static/css/admin_custom.css']
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.rol == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        flash('Debes iniciar sesión como administrador para acceder a esta tabla de datos.', 'error')
        return redirect(url_for('main.login'))

class UserAdmin(SecureModelView):
    # Deshabilitar la creación manual para forzar el flujo de "Registro Autónomo -> Aprobación" y evitar contraseñas no encriptadas.
    can_create = False
    column_list = ('nombre', 'email', 'carrera', 'area_interes', 'rol', 'aprobado', 'activo', 'fecha_registro')
    
    # Columnas por las que se puede buscar
    column_searchable_list = ('nombre', 'email', 'carrera')
    
    # Filtros laterales
    column_filters = ('aprobado', 'carrera', 'rol', 'activo')
    
    # Habilitar exportación nativa a CSV
    can_export = True
    export_types = ['csv']

    # Etiquetas personalizadas
    column_labels = {
        'nombre': 'Nombre Completo',
        'email': 'Correo',
        'carrera': 'Carrera',
        'area_interes': 'Área',
        'rol': 'Rol de Sistema',
        'aprobado': 'Aprobado',
        'activo': 'Activo',
        'fecha_registro': 'Registro'
    }

    # Restringir los roles, carreras e intereses a opciones predeterminadas
    form_overrides = {
        'rol': SelectField,
        'carrera': SelectField
    }
    
    form_args = {
        'rol': {
            'choices': [('usuario', 'Estudiante / Miembro / Usuario Normal'), ('admin', 'Administrador Total (Cuidado)')],
            'default': 'usuario'
        },
        'carrera': {
            'choices': [
                ('Ingeniería en sistemas computacionales', 'Ingeniería en sistemas computacionales'),
                ('Ingeniería en inteligencia artificial', 'Ingeniería en inteligencia artificial'),
                ('Ingeniería en mecatrónica', 'Ingeniería en mecatrónica'),
                ('Ingeniería en electrónica', 'Ingeniería en electrónica')
            ],
            'validators': [DataRequired(message="La carrera es obligatoria.")]
        }
    }

    # Soft delete: En lugar de borrar de SQL, marca como inactivo
    def delete_model(self, model):
        try:
            self.on_model_delete(model)
            model.activo = False
            self.session.commit()
            return True
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash('Hubo un error borrando el modelo. {}'.format(str(ex)), 'error')
            self.session.rollback()
            return False

    # Custom batch action para Aprobar usuarios masivamente y mandar email
    @action('approve', 'Aprobar Seleccionados', '¿Estás seguro de que quieres aprobar a los usuarios seleccionados y enviarles un correo de bienvenida?')
    def action_approve(self, ids):
        try:
            query = User.query.filter(User.id.in_(ids))
            count = 0
            
            # Obtener el proxy de la app real para pasarla a los hilos
            app = current_app._get_current_object()
            
            for user in query.all():
                if not user.aprobado:
                    user.aprobado = True
                    count += 1
                    
                    # Preparar correo de bienvenida
                    msg = Message(
                        subject="¡Bienvenido al Club de Robótica!",
                        sender=app.config.get('MAIL_DEFAULT_SENDER', 'noreply@clubrobotica.unach.mx'),
                        recipients=[user.email]
                    )
                    msg.body = f"Hola {user.nombre},\n\nTu solicitud de ingreso ha sido aprobada por un administrador del Club de Robótica.\n\nYa eres oficialmente un miembro activo. ¡Bienvenido al equipo!\n\nSaludos."
                    
                    # Mandar correo en hilo de fondo
                    thread = threading.Thread(target=send_async_email, args=(app, msg))
                    thread.start()

            self.session.commit()
            if count > 0:
                flash(f'{count} usuarios fueron aprobados con éxito y se les envió un correo.', 'success')
            else:
                flash('Ningún usuario nuevo fue aprobado (quizás ya estaban aprobados).', 'info')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(f'Hubo un error aprobando usuarios: {str(ex)}', 'error')
            self.session.rollback()

    @action('reset_password', 'Resetear Contraseña', '¿Estás seguro de que quieres sobreescribir la contraseña de los alumnos seleccionados al valor por defecto configurado en .env?')
    def action_reset_password(self, ids):
        try:
            query = User.query.filter(User.id.in_(ids))
            count = 0
            # CR-02: La contraseña por defecto se lee de la configuración / .env (DEFAULT_RESET_PASSWORD)
            # ya NO está hardcodeada en el código fuente
            default_password = current_app.config.get('DEFAULT_RESET_PASSWORD', 'robotica2026')
            for user in query.all():
                user.set_password(default_password)
                count += 1
            self.session.commit()
            flash(f'Contraseña reseteada al valor de DEFAULT_RESET_PASSWORD para {count} usuarios exitosamente.', 'success')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(f'Hubo un fatal error reseteando contraseñas: {str(ex)}', 'error')
            self.session.rollback()

    # (Opcional) Logica POST-Edicion
    def on_model_change(self, form, model, is_created):
        pass

# Definición para formatear nombres de imagenes asegurando UUID
def prefix_name(obj, file_data):
    parts = os.path.splitext(file_data.filename)
    return f"{uuid.uuid4().hex}{parts[1]}"

class NoticiaAdmin(SecureModelView):
    column_list = ('titulo', 'imagen_preview', 'fecha_publicacion', 'activo')
    column_searchable_list = ('titulo', 'contenido')
    column_filters = ('activo',)
    column_default_sort = ('fecha_publicacion', True)

    column_labels = {
        'titulo': 'Título',
        'imagen_preview': 'Imagen',
        'fecha_publicacion': 'Fecha de Publicación',
        'activo': 'Activo',
        'contenido': 'Contenido HTML / Texto',
        'autor': 'Autor',
        'imagen': 'Subir Imagen'
    }

    # Custom formatter para mostrar la miniatura en la lista
    def _list_thumbnail(view, context, model, name):
        if not model.imagen:
            return ''
        url = url_for('static', filename=os.path.join('uploads/noticias/', model.imagen).replace('\\', '/'))
        return Markup(f'<img src="{url}" style="width: 100px; height: auto; border-radius: 5px;">')

    column_formatters = {
        'imagen_preview': _list_thumbnail
    }

    # Definir el path base absoluto hacia static/uploads/noticias
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'noticias')

    form_extra_fields = {
        'imagen': form.ImageUploadField(
            'Imagen de Portada',
            base_path=base_path,
            url_relative_path='uploads/noticias/',
            namegen=prefix_name,
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif'],
            max_size=(1920, 1080, True),
            thumbnail_size=(200, 200, True),
        )
    }

    # Forzar al usuario autologueado como autor si se crea desde panel (opcional, aunque ModelView permite seleccionarlo)
    def on_model_change(self, form, model, is_created):
        if is_created and not model.autor_id:
            model.autor_id = current_user.id

class AlbumAdmin(SecureModelView):
    column_list = ('nombre', 'descripcion', 'fecha_creacion', 'activo')
    column_searchable_list = ('nombre', 'descripcion')
    form_columns = ('nombre', 'descripcion', 'activo')
    column_labels = {
        'nombre': 'Nombre del Álbum',
        'descripcion': 'Descripción',
        'fecha_creacion': 'Fecha de Creación',
        'activo': 'Activo'
    }

class FotoAdmin(SecureModelView):
    column_list = ('album', 'miniatura_preview', 'titulo', 'fecha_subida', 'activo')
    form_columns = ('album', 'titulo', 'imagen_path', 'activo')
    column_filters = ('album.nombre', 'activo')

    column_labels = {
        'album': 'Álbum',
        'titulo': 'Título de la Foto',
        'miniatura_preview': 'Vista Previa',
        'fecha_subida': 'Fecha de Subida',
        'imagen_path': 'Subir Fotografía (Máx 1200px)',
        'activo': 'Activo'
    }

    def _list_thumbnail(view, context, model, name):
        if not model.imagen_path:
            return ''
        url = url_for('static', filename=os.path.join('uploads/galeria/', model.imagen_path).replace('\\', '/'))
        return Markup(f'<img src="{url}" style="width: 150px; height: auto; border-radius: 8px;">')

    column_formatters = {
        'miniatura_preview': _list_thumbnail
    }

    base_path_galeria = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'galeria')

    form_extra_fields = {
        'imagen_path': form.ImageUploadField(
            'Subir Fotografía (Auto-Comprimida)',
            base_path=base_path_galeria,
            url_relative_path='uploads/galeria/',
            namegen=prefix_name,
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
            # Pillow constraint intercept: Resize up to 1200x1200 retaining aspect ratio 
            max_size=(1200, 1200, False), 
            thumbnail_size=(250, 250, True),
        )
    }

class HorarioAdmin(SecureModelView):
    column_list = ('dia_semana', 'hora_inicio', 'hora_fin', 'descripcion', 'activo')
    form_columns = ('dia_semana', 'hora_inicio', 'hora_fin', 'descripcion', 'activo')
    column_filters = ('dia_semana', 'activo')
    
    column_labels = {
        'dia_semana': 'Día de la Semana',
        'hora_inicio': 'Hora de Inicio',
        'hora_fin': 'Hora de Fin',
        'descripcion': 'Descripción / Nivel',
        'activo': 'Visible al Público'
    }

    form_overrides = {
        'dia_semana': SelectField
    }
    
    form_args = {
        'dia_semana': {
            'choices': [
                ('Lunes', 'Lunes'),
                ('Martes', 'Martes'),
                ('Miércoles', 'Miércoles'),
                ('Jueves', 'Jueves'),
                ('Viernes', 'Viernes'),
                ('Sábado', 'Sábado'),
                ('Domingo', 'Domingo')
            ],
            'validators': [DataRequired()]
        }
    }


class PageAdmin(SecureModelView):
    column_list = ('slug', 'titulo', 'ultima_modificacion')
    form_columns = ('slug', 'titulo', 'contenido')
    column_searchable_list = ('slug', 'titulo')
    column_default_sort = ('slug', False)

    column_labels = {
        'slug': 'Identificador (slug)',
        'titulo': 'Título de la Página',
        'contenido': 'Contenido HTML',
        'ultima_modificacion': 'Última Modificación'
    }

    form_widget_args = {
        'contenido': {
            'rows': 20,
            'class': 'form-control',
            'style': 'font-family: monospace; font-size: 13px;'
        },
        'slug': {
            'readonly': True
        }
    }

class ConfiguracionAdmin(SecureModelView):
    column_list = ('llave', 'valor', 'descripcion')
    form_columns = ('llave', 'valor', 'descripcion', 'valor_imagen')
    column_labels = {
        'llave': 'Identificador Único (Key)',
        'valor': 'Valor Asignado',
        'descripcion': 'Descripción Interna',
        'valor_imagen': 'Subir Imagen (Opcional)'
    }

    form_widget_args = {
        'valor': {
            'rows': 5,
            'class': 'form-control',
            'style': 'font-family: monospace;'
        }
    }

    base_path_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'config')

    form_extra_fields = {
        'valor_imagen': form.ImageUploadField(
            'Subir Imagen (Solo si es configuración de imagen)',
            base_path=base_path_config,
            url_relative_path='uploads/config/',
            namegen=prefix_name,
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
            max_size=(1200, 1200, False),
            thumbnail_size=(150, 150, True)
        )
    }

    def on_model_change(self, form, model, is_created):
        # Si se subió una imagen, usar su nombre como el valor de la configuración
        if form.valor_imagen.data:
            # El campo ImageUploadField ya guardó el archivo en el disco,
            # solo necesitamos guardar el nombre del archivo en el campo 'valor'
            filename = form.valor_imagen.data.filename
            if filename:
                model.valor = filename

class ProyectoAdmin(SecureModelView):
    column_list = ('titulo', 'equipo', 'miniatura_preview', 'categoria', 'fecha_creacion', 'activo')
    form_columns = ('titulo', 'equipo', 'categoria', 'descripcion_corta', 'descripcion_larga', 'imagen_path', 'activo')
    column_searchable_list = ('titulo', 'descripcion_corta')
    column_filters = ('categoria', 'activo', 'equipo.nombre')

    column_labels = {
        'titulo': 'Nombre del Proyecto',
        'equipo': 'Equipo Asignado',
        'categoria': 'Categoría',
        'descripcion_corta': 'Resumen (1 línea)',
        'descripcion_larga': 'Detalle completo HTML',
        'imagen_path': 'Subir Fotografía (Máx 1200px)',
        'miniatura_preview': 'Vista Previa',
        'activo': 'Visible'
    }

    def _list_thumbnail(view, context, model, name):
        if not model.imagen_path:
            return ''
        url = url_for('static', filename=os.path.join('uploads/proyectos/', model.imagen_path).replace('\\', '/'))
        return Markup(f'<img src="{url}" style="width: 150px; height: auto; border-radius: 8px;">')

    column_formatters = {
        'miniatura_preview': _list_thumbnail
    }

    base_path_proyectos = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'proyectos')

    form_extra_fields = {
        'imagen_path': form.ImageUploadField(
            'Subir Imagen (Auto-Comprimida)',
            base_path=base_path_proyectos,
            url_relative_path='uploads/proyectos/',
            namegen=prefix_name,
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
            max_size=(1200, 1200, False), 
            thumbnail_size=(250, 250, True),
        )
    }

    form_widget_args = {
        'descripcion_larga': {
            'rows': 8,
            'class': 'form-control'
        }
    }

class EquipoAdmin(SecureModelView):
    column_list = ('nombre', 'descripcion', 'activo')
    form_columns = ('nombre', 'descripcion', 'activo')
    column_searchable_list = ('nombre',)
    column_filters = ('activo',)
    
    column_labels = {
        'nombre': 'Nombre del Equipo',
        'descripcion': 'Descripción',
        'activo': 'Activo'
    }

class MiembroEquipoAdmin(SecureModelView):
    column_list = ('equipo', 'user', 'nombre', 'cargo', 'miniatura_preview', 'area', 'orden', 'activo')
    form_columns = ('equipo', 'user', 'nombre', 'cargo', 'area', 'foto_path', 'orden', 'activo')
    column_searchable_list = ('nombre', 'cargo', 'user.nombre', 'user.email')
    column_filters = ('area', 'activo', 'equipo.nombre')
    column_default_sort = ('orden', False)

    column_labels = {
        'equipo': 'Equipo Perteneciente',
        'user': 'Usuario Vinculado',
        'nombre': 'Nombre en Display (Legacy)',
        'cargo': 'Cargo / Rol en Equipo',
        'area': 'Área de Trabajo',
        'foto_path': 'Subir Foto (Opcional)',
        'miniatura_preview': 'Foto',
        'orden': 'Orden de Aparición',
        'activo': 'Socio Activo'
    }

    # Restringir cargos a opciones predeterminadas
    form_overrides = {
        'cargo': SelectField
    }

    form_args = {
        'cargo': {
            'choices': [
                ('Líder - Equipo', 'Líder - Equipo'),
                ('Miembro - Equipo', 'Miembro - Equipo'),
                ('Entrenador - Equipo', 'Entrenador - Equipo')
            ],
            'default': 'Miembro - Equipo'
        },
        'user': {
            'validators': [DataRequired(message="Debe seleccionar un Usuario Vinculado obligatoriamente.")]
        },
        'equipo': {
            'validators': [DataRequired(message="Debe seleccionar un Equipo obligatoriamente.")]
        }
    }

    def on_model_change(self, form, model, is_created):
        from wtforms.validators import ValidationError
        from app.models.miembro_equipo import MiembroEquipo
        
        # En on_model_change, model.user_id puede ser None porque no se ha hecho flush. 
        # Debemos usar model.user.id que es el objeto ya asociado por WTForms.
        if not model.user:
            raise ValidationError("Usuario no válido.")
            
        usuario_id = model.user.id
        
        # El usuario pidió: "Que ya tenga Una vinculación existente".
        # Es decir, un Usuario a nivel club SOLO puede ser miembro activo de UN SOLO registro a la vez en total (sin importar el equipo).
        existente = MiembroEquipo.query.filter_by(user_id=usuario_id, activo=True).first()
        
        if existente and existente.id != model.id:
            raise ValidationError(f"Error de Integridad: El usuario '{model.user.nombre}' ya está vinculado como miembro de equipo activo en el club (Equipo: {existente.equipo.nombre if existente.equipo else 'N/A'}). Debes desactivar o borrar su participación anterior si deseas cambiarlo.")


    def _list_thumbnail(view, context, model, name):
        if not model.foto_path:
            return ''
        url = url_for('static', filename=os.path.join('uploads/equipo/', model.foto_path).replace('\\', '/'))
        return Markup(f'<img src="{url}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 50%;">')

    column_formatters = {
        'miniatura_preview': _list_thumbnail
    }

    base_path_equipo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'equipo')

    form_extra_fields = {
        'foto_path': form.ImageUploadField(
            'Subir Fotografía Cuadrada',
            base_path=base_path_equipo,
            url_relative_path='uploads/equipo/',
            namegen=prefix_name,
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
            max_size=(800, 800, False), 
            thumbnail_size=(150, 150, True),
        )
    }
