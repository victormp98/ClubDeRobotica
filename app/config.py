import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail Config
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.fake-server.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    # ME-03: parsear correctamente el string 'true'/'false' de la variable de entorno
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'dummy@example.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'dummy-password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@clubrobotica.unach.mx'

    # ME-02 / AL-03: Correo del administrador (configurable via .env)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@clubrobotica.unach.mx'

    # CR-02: Contraseña temporal para reset masivo (configurable via .env)
    DEFAULT_RESET_PASSWORD = os.environ.get('DEFAULT_RESET_PASSWORD') or 'robotica2026'
