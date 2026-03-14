from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash
from app.models.user import User

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

    # (Opcional) Logica POST-Edicion: si cambia `aprobado` a True de repente, ideal mandar email de bienvenida.
    def on_model_change(self, form, model, is_created):
        # Cuando se actualiza un usuario y se aprueba por primera vez
        pass # Por ahora no lo conectaré a Mailer para no complicar dependencias cruzadas en admin_views
