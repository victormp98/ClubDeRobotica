from app.extensions import db

class CategoriaTorneo(db.Model):
    __tablename__ = 'categoria_torneo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edades = db.Column(db.String(100))
    mision = db.Column(db.Text)
    imagen_path = db.Column(db.String(255))
    orden = db.Column(db.Integer, default=0)

class FechaTorneo(db.Model):
    __tablename__ = 'fecha_torneo'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    estado_clase = db.Column(db.String(50))
    estado_etiqueta = db.Column(db.String(100))
    orden = db.Column(db.Integer, default=0)

class RecuadroTorneo(db.Model):
    __tablename__ = 'recuadro_torneo'
    id = db.Column(db.Integer, primary_key=True)
    icono = db.Column(db.String(100))
    etiqueta = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.String(100), nullable=False)
    orden = db.Column(db.Integer, default=0)

class RequisitoTorneo(db.Model):
    __tablename__ = 'requisito_torneo'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    orden = db.Column(db.Integer, default=0)

class ProyectoTorneo(db.Model):
    __tablename__ = 'proyecto_torneo'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    imagen_path = db.Column(db.String(255))
    categoria = db.Column(db.String(100))
    orden = db.Column(db.Integer, default=0)
