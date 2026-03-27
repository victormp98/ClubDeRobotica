from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()
socketio = SocketIO()

login_manager.login_view = 'main.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta área exclusiva.'
login_manager.login_message_category = 'warning'
