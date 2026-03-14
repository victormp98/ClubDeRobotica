from app.extensions import db
from datetime import datetime, timezone

class Foto(db.Model):
    __tablename__ = 'fotos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    imagen_path = db.Column(db.String(255), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('albumes.id'), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    activo = db.Column(db.Boolean, default=True)

    album = db.relationship('Album', back_populates='fotos')

    def __repr__(self):
        return f'<Foto {self.titulo}>'
