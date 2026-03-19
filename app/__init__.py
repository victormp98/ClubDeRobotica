from flask import Flask
from markupsafe import Markup  # BA-02: import explícito (antes se usaba sin importar)
from .extensions import db, migrate
from .config import Config
from .cli import register_commands, auto_seed_admin

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Priority for application templates over library templates
    import os
    from jinja2 import ChoiceLoader, FileSystemLoader
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(os.path.join(app.root_path, 'templates', 'admin_overrides')),
        FileSystemLoader(os.path.join(app.root_path, 'templates')),
        app.jinja_loader
    ])

    # Initialize Flask extensions here
    db.init_app(app)
    migrate.init_app(app, db)
    
    from .extensions import mail, login_manager
    mail.init_app(app)
    login_manager.init_app(app)

    # Register blueprints here
    from app.views.main import main_bp
    app.register_blueprint(main_bp)

    # Ensure all models are imported so Alembic can detect them
    from app import models
    from app.models.user import User
    from app.models.noticia import Noticia
    from app.models.album import Album
    from app.models.foto import Foto
    from app.models.horario import Horario
    from app.models.page import Page
    from app.models.configuracion import Configuracion
    from app.models.proyecto import Proyecto
    from app.models.equipo import Equipo
    from app.models.miembro_equipo import MiembroEquipo
    from app.models.tarea import Tarea
    from app.models.columna import Columna
    from app.models.checklist_item import ChecklistItem
    from app.models.comentario import Comentario
    from app.models.adjunto import Adjunto
    from app.admin_views import UserAdmin, MyAdminIndexView, NoticiaAdmin, AlbumAdmin, FotoAdmin, HorarioAdmin, PageAdmin, ConfiguracionAdmin, ProyectoAdmin, EquipoAdmin, MiembroEquipoAdmin, WROConfigAdmin, TareaAdmin, ColumnaAdmin
    
    # Initialize Flask-Admin here (to avoid circular imports with models)
    from flask_admin import Admin
    from flask_admin.menu import MenuLink
    from flask_admin.theme import Bootstrap4Theme
    admin = Admin(app, name='Admin - Club de Robótica', url='/admin', index_view=MyAdminIndexView(), theme=Bootstrap4Theme(swatch='slate', base_template='master.html'))
    admin.add_view(UserAdmin(User, db.session, name='Usuarios', endpoint='users'))
    admin.add_view(NoticiaAdmin(Noticia, db.session, name='Noticias', endpoint='noticias'))
    
    admin.add_view(AlbumAdmin(Album, db.session, name='Álbumes', category='Galería', endpoint='albumes'))
    admin.add_view(FotoAdmin(Foto, db.session, name='Fotos', category='Galería', endpoint='fotos'))
    admin.add_view(ProyectoAdmin(Proyecto, db.session, name='Proyectos', category='Contenido', endpoint='proyectos'))
    admin.add_view(HorarioAdmin(Horario, db.session, name='Horarios', category='Contenido', endpoint='horarios'))
    admin.add_view(PageAdmin(Page, db.session, name='Páginas Estáticas', category='Contenido', endpoint='pages'))
    admin.add_view(EquipoAdmin(Equipo, db.session, name='Equipos', category='Contenido', endpoint='equipos'))
    admin.add_view(MiembroEquipoAdmin(MiembroEquipo, db.session, name='Miembros de Equipo', category='Contenido', endpoint='miembros_equipo'))
    admin.add_view(TareaAdmin(Tarea, db.session, name='Gestión de Tareas', category='Contenido', endpoint='tareas_admin'))
    
    admin.add_view(ConfiguracionAdmin(Configuracion, db.session, name='Configuración Global', category='Ajustes', endpoint='configuraciones'))
    admin.add_view(WROConfigAdmin(Configuracion, db.session, name='🏆 Gestión Certamen', endpoint='wro_config'))

    # Botones de navegación salida (MenuLink)
    admin.add_link(MenuLink(name='Volver al Sitio', url='/', icon_type='fa', icon_value='fa-home'))
    admin.add_link(MenuLink(name='Cerrar Sesión', url='/logout', icon_type='fa', icon_value='fa-sign-out'))
    
    @app.errorhandler(500)
    def handle_500(e):
        import traceback
        # CR-04: Traza solo en logs del servidor, NUNCA expuesta al navegador
        print("INTERNAL SERVER ERROR DETECTED:")
        traceback.print_exc()
        return "Error interno del servidor. Por favor contacta al administrador.", 500

    # Initialize image cleanup listeners
    from app.utils.image_cleanup import register_cleanup_listeners
    register_cleanup_listeners(db)

    # Register CLI commands
    register_commands(app)

    # Auto-seed admin on startup
    with app.app_context():
        auto_seed_admin(app)

    @app.context_processor
    def utility_processor():
        import json
        def safe_json(val, default=None):
            try:
                if not val: return default or {}
                return json.loads(val) if isinstance(val, str) else val
            except:
                return default or {}
        
        def get_tag_color(name):
            colors = {
                'blue': '#3b82f6',
                'green': '#22c55e',
                'yellow': '#eab308',
                'red': '#ef4444',
                'purple': '#a855f7',
                'teal': '#14b8a6',
                'default': 'rgba(255,255,255,0.2)'
            }
            return colors.get(name, colors['default'])
            
        return dict(safe_json=safe_json, get_tag_color=get_tag_color)

    return app
