from app import create_app
from app.extensions import db
from app.models.configuracion import Configuracion

app = create_app()
with app.app_context():
    configs = Configuracion.query.filter(Configuracion.llave.notlike('TORNEO_%')).all()
    print("GLOBAL_CONFIGURATIONS:")
    for c in configs:
        print(f"- {c.llave}: {c.descripcion}")
