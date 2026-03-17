import click
from flask.cli import with_appcontext
from flask import current_app
from app.extensions import db
from app.models.user import User

@click.command('seed-admin')
@with_appcontext
def seed_admin_command():
    """Crea el usuario administrador inicial si no existe."""
    email = current_app.config.get('INITIAL_ADMIN_EMAIL', 'admin@club.com')
    password = current_app.config.get('INITIAL_ADMIN_PASSWORD', 'admin123')
    
    click.echo(f"[*] Verificando existencia de administrador: {email}")
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        click.echo(f"[+] Creando nuevo administrador: {email}")
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
        click.echo("✓ Administrador creado exitosamente.")
    else:
        click.echo(f"[~] El administrador '{email}' ya existe. No se realizaron cambios.")

def register_commands(app):
    """Registra los comandos personalizados en la aplicación Flask."""
    app.cli.add_command(seed_admin_command)
