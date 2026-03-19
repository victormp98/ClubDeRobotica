from app.extensions import db
from datetime import datetime, timezone

class Adjunto(db.Model):
    __tablename__ = 'adjuntos'
    id = db.Column(db.Integer, primary_key=True)
    tarea_id = db.Column(db.Integer, db.ForeignKey('tareas.id'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta = db.Column(db.String(255), nullable=False)
    tipo_mimetype = db.Column(db.String(100))
    fecha_subida = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Adjunto {self.nombre_archivo}>'
