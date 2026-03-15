from app.extensions import db

class MiembroEquipo(db.Model):
    __tablename__ = 'equipo'
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Puede ser nulo por histórico
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)
    
    # Datos específicos del rol en este equipo
    nombre = db.Column(db.String(100), nullable=True) # Opcional si se toma del user_id
    cargo = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100))
    foto_path = db.Column(db.String(255)) # Opcional, podría sobrescribir la del user
    orden = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True) # Para Soft-Delete del miembro en el equipo

    # Relaciones de ORM
    equipo = db.relationship('Equipo', back_populates='miembros')
    user = db.relationship('User', backref='membresias_equipo') # Backref simple por ahora

    @property
    def display_name(self):
        return self.nombre if self.nombre else (self.user.nombre if self.user else 'Sin Nombre')

    @property
    def display_area(self):
        return self.area if self.area else (self.user.area_interes if self.user else '')

    def __repr__(self):
        nombre_mostrar = self.nombre if self.nombre else (self.user.nombre if self.user else 'Sin Nombre')
        equipo_nombre = self.equipo.nombre if self.equipo else 'Sin Equipo'
        return f'<MiembroEquipo {nombre_mostrar} - {self.cargo} ({equipo_nombre})>'
