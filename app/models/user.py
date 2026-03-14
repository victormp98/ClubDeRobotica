from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    carrera = db.Column(db.String(100))
    area_interes = db.Column(db.String(100))
    rol = db.Column(db.String(20), default='visitante') # admin, miembro, visitante
    aprobado = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    activo = db.Column(db.Boolean, default=True)

    noticias = db.relationship('Noticia', back_populates='autor', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'
