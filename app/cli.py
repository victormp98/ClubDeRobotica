import click
from flask.cli import with_appcontext
from flask import current_app
from app.extensions import db
from app.models.user import User

def get_admin_credentials(app):
    """Obtiene las credenciales del admin desde la configuración."""
    email = app.config.get('INITIAL_ADMIN_EMAIL', 'admin@club.com')
    password = app.config.get('INITIAL_ADMIN_PASSWORD', 'admin123')
    return email, password

def run_seed_logic(app, log_info, log_error):
    """Lógica compartida para crear el administrador."""
    try:
        email, password = get_admin_credentials(app)
        log_info(f"[*] Verificando existencia de administrador: {email}")
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            log_info(f"[+] Creando nuevo administrador: {email}")
            admin = User(
                nombre="Administrador Principal",
                email=email,
                rol='admin',
                aprobado=True,
                activo=True
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            log_info("✓ Administrador creado exitosamente.")
        else:
            log_info(f"[~] El administrador '{email}' ya existe. No se realizaron cambios.")
    except Exception as e:
        log_error(f"Error durante la creación automática del administrador: {str(e)}")

@click.command('seed-admin')
@with_appcontext
def seed_admin_command():
    """Crea el usuario administrador inicial si no existe."""
    from flask import current_app
    run_seed_logic(current_app, click.echo, click.echo)

def auto_seed_admin(app):
    """Función para ejecutar automáticamente al inicio de la app."""
    # Usamos el logger de la app para la salida
    run_seed_logic(app, app.logger.info, app.logger.error)

def register_commands(app):
    """Registra los comandos personalizados en la aplicación Flask."""
    app.cli.add_command(seed_admin_command)
