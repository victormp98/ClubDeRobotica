from app.extensions import db

class Horario(db.Model):
    __tablename__ = 'horarios'
    id = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.String(20), nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    descripcion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Horario {self.dia_semana} {self.hora_inicio}-{self.hora_fin}>'
