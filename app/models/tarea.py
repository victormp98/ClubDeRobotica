from app.extensions import db
from datetime import datetime, timezone

class Tarea(db.Model):
    __tablename__ = 'tareas'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    
    # Columna asociada (Estado en el Kanban)
    columna_id = db.Column(db.Integer, db.ForeignKey('columnas.id'), nullable=False)
    
    # Prioridades: baja, media, alta
    prioridad = db.Column(db.String(20), default='media')
    
    # Color de la tarjeta (para personalización en el Kanban)
    color = db.Column(db.String(30), default='default')
    
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_limite = db.Column(db.DateTime, nullable=True)
    
    # Campo para etiquetas (JSON string): {'blue': 'Tag Name', ...}
    etiquetas = db.Column(db.Text, default='{}')
    
    # Relaciones
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=False)
    asignado_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    proyecto = db.relationship('Proyecto', backref=db.backref('tareas_all', lazy=True))
    asignado = db.relationship('User', backref=db.backref('tareas_asignadas', lazy=True))

    # Nuevas relaciones para funcionalidades extendidas
    checklist = db.relationship('ChecklistItem', backref='tarea', lazy=True, cascade="all, delete-orphan")
    comentarios = db.relationship('Comentario', backref='tarea', lazy=True, cascade="all, delete-orphan")
    adjuntos = db.relationship('Adjunto', backref='tarea', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Tarea {self.titulo} (ID: {self.id})>'
