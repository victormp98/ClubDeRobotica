from run import app
from app.extensions import db
from app.models.configuracion import Configuracion

with app.app_context():
    count = Configuracion.query.filter(Configuracion.llave.in_([
        'TORNEO_CATEGORIAS', 'TORNEO_FECHAS', 'TORNEO_PROYECTOS', 'TORNEO_REQUISITOS', 'TORNEO_RECUADROS'
    ])).delete(synchronize_session=False)
    db.session.commit()
    print(f"Limpieza finalizada: Se eliminaron {count} variables JSON obsoletas.")
