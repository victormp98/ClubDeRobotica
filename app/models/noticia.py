from app.extensions import db
from datetime import datetime, timezone

class Noticia(db.Model):
    __tablename__ = 'noticias'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_publicacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    autor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    imagen = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)

    autor = db.relationship('User', back_populates='noticias')

    def __repr__(self):
        return f'<Noticia {self.titulo}>'
