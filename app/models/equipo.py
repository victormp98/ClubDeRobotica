from app.extensions import db

class Equipo(db.Model):
    __tablename__ = 'equipos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)

    # Relación con MiembroEquipo
    miembros = db.relationship('MiembroEquipo', back_populates='equipo', lazy=True)

    def __repr__(self):
        return f'<Equipo {self.nombre}>'
