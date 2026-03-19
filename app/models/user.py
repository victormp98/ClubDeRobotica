from app.extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timezone
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    # ME-04: Query.get() deprecado en SQLAlchemy 2.x -> usar db.session.get()
    return db.session.get(User, int(user_id))

class User(UserMixin, db.Model):
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

    @property
    def is_active(self):
        return self.activo

    @property
    def es_miembro_equipo(self):
        """Verifica si el usuario pertenece a al menos un equipo activo."""
        # membresias_equipo es el backref definido en MiembroEquipo
        return any(m.activo for m in self.membresias_equipo)

    def get_reset_password_token(self, expires_in=3600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': datetime.now(timezone.utc).timestamp() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except ExpiredSignatureError:
            # ME-01: Token expirado — devolver None sin propagar la excepción
            return None
        except InvalidTokenError:
            # ME-01: Token inválido, manipulado o con formato incorrecto
            return None
        # ME-04: Query.get() deprecado en SQLAlchemy 2.x -> usar db.session.get()
        return db.session.get(User, id)

    def __repr__(self):
        return self.nombre
