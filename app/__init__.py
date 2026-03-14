from flask import Flask
from .extensions import db, migrate
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

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
    from app.admin_views import UserAdmin, MyAdminIndexView, NoticiaAdmin
    
    # Initialize Flask-Admin here (to avoid circular imports with models)
    from flask_admin import Admin
    admin = Admin(app, name='Admin - Club de Robótica', url='/admin', index_view=MyAdminIndexView())
    admin.add_view(UserAdmin(User, db.session, name='Usuarios', endpoint='users'))
    admin.add_view(NoticiaAdmin(Noticia, db.session, name='Noticias', endpoint='noticias'))

    return app
