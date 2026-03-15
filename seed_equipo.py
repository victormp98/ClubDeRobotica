from app import create_app
from app.extensions import db
from app.models.equipo import Equipo
from app.models.miembro_equipo import MiembroEquipo
from app.models.user import User

def seed_default_equipo():
    app = create_app()
    with app.app_context():
        # 1. Crear Equipo por defecto
        equipo_titulares = Equipo.query.filter_by(nombre="Titulares").first()
        if not equipo_titulares:
            equipo_titulares = Equipo(nombre="Titulares", descripcion="Equipo principal del club.")
            db.session.add(equipo_titulares)
            db.session.flush()
            print("Creado equipo Titulares.")
        
        # 2. Vincular miembros existentes
        miembro = MiembroEquipo.query.get(1)
        if miembro:
            miembro.equipo_id = equipo_titulares.id
            # Vincular al User 1 (admin principal)
            miembro.user_id = 1
            print(f"Vinculado el miembro '{miembro.nombre}' al equipo '{equipo_titulares.nombre}' y al usuario ID 1.")
        
        db.session.commit()
        print("Migración de datos completada exitosamente.")

if __name__ == '__main__':
    seed_default_equipo()
