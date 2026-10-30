"""
Script de inicialización de administrador.
Verifica si el administrador principal existe; si no, lo crea.
Seguro para correr múltiples veces (idempotente).
"""
import sys
import os

# Asegurar que el directorio raíz esté en el path para importar 'app'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User

def seed_admin():
    app = create_app()
    with app.app_context():
        # Configuración privada requerida para la creación de la cuenta inicial.
        email = app.config.get('INITIAL_ADMIN_EMAIL')
        password = app.config.get('INITIAL_ADMIN_PASSWORD')
        if not email or not password:
            raise RuntimeError('Configura INITIAL_ADMIN_EMAIL y INITIAL_ADMIN_PASSWORD antes de crear el administrador.')
        
        print(f"[*] Verificando existencia de administrador: {email}")
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"[+] Creando nuevo administrador: {email}")
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
            print("[✓] Administrador creado exitosamente.")
        else:
            print(f"[~] El administrador '{email}' ya existe. No se realizaron cambios.")

if __name__ == "__main__":
    seed_admin()
