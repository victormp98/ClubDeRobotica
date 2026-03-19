from app.extensions import db

class Columna(db.Model):
    __tablename__ = 'columnas'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    orden = db.Column(db.Integer, default=0)
    
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=False)
    
    # Tareas asociadas a esta columna
    tareas = db.relationship('Tarea', backref='columna_obj', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'{self.titulo} (Proy: {self.proyecto_id})'
