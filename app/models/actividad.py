from datetime import datetime
from app import db

class Actividad(db.Model):
    __tablename__ = 'actividad'
    __table_args__ = {'extend_existing': True}

    id_actividad = db.Column(db.Integer, primary_key=True)
    fecha_actividad = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    tipo_actividad = db.Column(db.String(50), nullable=False, default='MONITOREO')
    id_comunidad = db.Column(db.Integer, db.ForeignKey('comunidad.id_comunidad'), nullable=False, default=1)
    id_nivel = db.Column(db.Integer, db.ForeignKey('nivel.id_nivel'), nullable=True, default=1)
    id_usuario = db.Column(db.Integer, nullable=True, default=4)

    # Campos de soporte y evidencias
    descripcion = db.Column(db.Text, nullable=True)
    poblacion = db.Column(db.Integer, default=0)
    acuerdos = db.Column(db.Text, nullable=True)
    minuta_archivo = db.Column(db.String(255), nullable=True)

    # Aliases
    @property
    def id(self):
        return self.id_actividad

    @property
    def fecha(self):
        return self.fecha_actividad

    @property
    def actividad(self):
        return self.tipo_actividad

    # Relaciones relacionales del ONCC
    comunidad = db.relationship('ComunidadActiva', backref='actividades_oncc', lazy=True)
    nivel = db.relationship('NivelActivo', backref='actividades_oncc', lazy=True)
    
    monitoreo = db.relationship('Monitoreo', backref='actividad_rel', uselist=False, cascade="all, delete-orphan")
    tecnicos_asociados = db.relationship('ActividadTecnico', backref='actividad_rel', cascade="all, delete-orphan")
    imagenes_asociadas = db.relationship('ImagenesActividad', backref='actividad_rel', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Actividad {self.tipo_actividad} ({self.id_actividad})>"


class Imagenes(db.Model):
    __tablename__ = 'imagenes'
    __table_args__ = {'extend_existing': True}

    id_imagen = db.Column(db.BigInteger, primary_key=True)
    url_imagen = db.Column(db.Text, nullable=False)
    nombre_imagen = db.Column(db.String(100), nullable=False)
    fecha_imagen = db.Column(db.Date, nullable=False, default=datetime.utcnow)


class ImagenesActividad(db.Model):
    __tablename__ = 'imagenes_actividad'
    __table_args__ = {'extend_existing': True}

    id_imagenes_actividad = db.Column(db.Integer, primary_key=True)
    id_imagen = db.Column(db.BigInteger, db.ForeignKey('imagenes.id_imagen'), nullable=False)
    id_actividad = db.Column(db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False)

    imagen = db.relationship('Imagenes', backref='actividad_vinculo')


class ActividadTecnico(db.Model):
    __tablename__ = 'actividad_tecnico'
    __table_args__ = {'extend_existing': True}

    id_actividad_tecnico = db.Column(db.Integer, primary_key=True)
    id_actividad = db.Column(db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False)
    id_tecnico = db.Column(db.Integer, db.ForeignKey('tecnicos.id_tecnico'), nullable=False)

    tecnico = db.relationship('Tecnico', backref='actividades_asignadas')


class Monitoreo(db.Model):
    __tablename__ = 'monitoreo'
    __table_args__ = {'extend_existing': True}

    id_monitoreo = db.Column(db.Integer, primary_key=True)
    id_actividad = db.Column(db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False, unique=True)
    nombre_monitoreo = db.Column(db.String(100), nullable=False)
    tipo_actividad = db.Column(db.String(50), nullable=False, default='MONITOREO')