from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask_admin import form
from flask_login import current_user
from flask import redirect, url_for, flash, current_app
from markupsafe import Markup
from flask_mail import Message
from app.models.user import User
from app.models.noticia import Noticia
from app.extensions import mail
import threading
import sys
import traceback
import os
import uuid
from app.extensions import mail
import threading
import sys
import traceback

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print(f"[MAIL_SUCCESS] Correo enviado a {msg.recipients}")
        except Exception as e:
            print(f"[MAIL_ERROR] No se pudo enviar el correo a {msg.recipients}. Credenciales dummy.")
            print(traceback.format_exc(), file=sys.stderr)

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.rol == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        flash('Debes iniciar sesión para acceder al panel de control.', 'error')
        return redirect(url_for('main.admin_login'))

    @expose('/')
    def index(self):
        pendientes_count = User.query.filter_by(aprobado=False, activo=True).count()
        activos_count = User.query.filter_by(aprobado=True, activo=True).count()
        return self.render('admin/index.html', pendientes_count=pendientes_count, activos_count=activos_count)

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.rol == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        flash('Debes iniciar sesión como administrador para acceder a esta página.', 'error')
        return redirect(url_for('main.admin_login'))

class UserAdmin(SecureModelView):
    # Columnas visibles en la lista
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
        'rol': 'Rol',
        'aprobado': 'Aprobado',
        'activo': 'Activo',
        'fecha_registro': 'Registro'
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

