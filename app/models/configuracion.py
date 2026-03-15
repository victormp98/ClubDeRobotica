from app.extensions import db

class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    llave = db.Column(db.String(100), primary_key=True)
    valor = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Configuracion {self.llave}={self.valor[:20]}>'
