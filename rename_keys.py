from run import app
from app.extensions import db
from app.models.configuracion import Configuracion

with app.app_context():
    configs = Configuracion.query.filter(Configuracion.llave.like('WRO_%')).all()
    count = 0
    for c in configs:
        new_key = c.llave.replace('WRO_', 'TORNEO_')
        # Check if the new key already exists to prevent duplicate key errors
        existing = Configuracion.query.get(new_key)
        if existing:
            # Overwrite if we are replacing, or just delete the old one
            db.session.delete(c)
        else:
            c.llave = new_key
        count += 1
    db.session.commit()
    print(f"Renombrados o fusionados {count} registros WRO_ a TORNEO_")
