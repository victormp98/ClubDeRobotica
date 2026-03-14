from flask import Flask
from .extensions import db, migrate
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    migrate.init_app(app, db)
    
    from .extensions import mail
    mail.init_app(app)

    # Register blueprints here
    from app.views.main import main_bp
    app.register_blueprint(main_bp)

    # Ensure all models are imported so Alembic can detect them
    from app import models

    return app
