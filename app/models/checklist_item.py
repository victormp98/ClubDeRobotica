from app.extensions import db

class ChecklistItem(db.Model):
    __tablename__ = 'checklist_items'
    id = db.Column(db.Integer, primary_key=True)
    tarea_id = db.Column(db.Integer, db.ForeignKey('tareas.id'), nullable=False)
    texto = db.Column(db.String(255), nullable=False)
    completado = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ChecklistItem {self.texto} - {"Ok" if self.completado else "Pending"}>'
