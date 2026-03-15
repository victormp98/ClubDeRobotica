from app.extensions import db
from datetime import datetime, timezone

class Proyecto(db.Model):
    __tablename__ = 'proyectos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    descripcion_corta = db.Column(db.String(255), nullable=False)
    descripcion_larga = db.Column(db.Text)
    imagen_path = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    activo = db.Column(db.Boolean, default=True)

    # Relación con Equipo (Opcional, un proyecto puede no tener equipo aún o ser independiente)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)
    equipo = db.relationship('Equipo', backref='proyectos')

    def __repr__(self):
        return f'<Proyecto {self.titulo}>'
