from app.extensions import db
from datetime import datetime, timezone

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, primary_key=True)
    tarea_id = db.Column(db.Integer, db.ForeignKey('tareas.id'), nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cuerpo = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    autor = db.relationship('User', backref=db.backref('comentarios_kanban', lazy=True))

    def __repr__(self):
        return f'<Comentario por {self.autor_id} en tarea {self.tarea_id}>'
