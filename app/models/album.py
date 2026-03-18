from app.extensions import db
from datetime import datetime, timezone

class Album(db.Model):
    __tablename__ = 'albumes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    activo = db.Column(db.Boolean, default=True)
    
    # NUEVOS: Campos de Privacidad (v2)
    es_publico = db.Column(db.Boolean, default=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=True)

    fotos = db.relationship('Foto', back_populates='album', lazy=True, cascade="all, delete-orphan")
    proyecto = db.relationship('Proyecto', back_populates='albumes')

    def __repr__(self):
        return f'<Album {self.nombre}>'
