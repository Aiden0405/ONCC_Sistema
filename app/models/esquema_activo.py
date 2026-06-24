from app import db

class EstadoActivo(db.Model):
    __tablename__ = 'estado'
    __table_args__ = {'extend_existing': True}

    id_estado = db.Column(db.Integer, primary_key=True)
    nombre_estado = db.Column(db.String(80), nullable=False)


class MunicipioActivo(db.Model):
    __tablename__ = 'municipio'
    __table_args__ = {'extend_existing': True}

    id_municipio = db.Column(db.Integer, primary_key=True)
    id_estado = db.Column(db.Integer, db.ForeignKey('estado.id_estado'), nullable=False)
    nombre_municipio = db.Column(db.String(120), nullable=False)

    estado = db.relationship('EstadoActivo', backref=db.backref('municipios', lazy='dynamic'))


class ParroquiaActiva(db.Model):
    __tablename__ = 'parroquia'
    __table_args__ = {'extend_existing': True}

    id_parroquia = db.Column(db.Integer, primary_key=True)
    id_municipio = db.Column(db.Integer, db.ForeignKey('municipio.id_municipio'), nullable=False)
    nombre_parroquia = db.Column(db.String(120), nullable=False)

    municipio = db.relationship('MunicipioActivo', backref=db.backref('parroquias', lazy='dynamic'))


class InstitucionActiva(db.Model):
    __tablename__ = 'intitucion'
    __table_args__ = {'extend_existing': True}

    id_institucion = db.Column(db.Integer, primary_key=True)
    nombre_institucion = db.Column(db.String(50), nullable=False)
    id_comunidad = db.Column(db.Integer, db.ForeignKey('comunidad.id_comunidad'), nullable=False)
    tipo_intitucion = db.Column(db.String(20), nullable=False)
    direccion_exacta = db.Column(db.String(100), nullable=False)
    numero_contacto = db.Column(db.String(25), nullable=False)
    correo_electronico = db.Column(db.String(40), nullable=False)


class ComunidadActiva(db.Model):
    __tablename__ = 'comunidad'
    __table_args__ = {'extend_existing': True}

    id_comunidad = db.Column(db.Integer, primary_key=True)
    id_parroquia = db.Column(db.Integer, db.ForeignKey('parroquia.id_parroquia'), nullable=False)
    nombre_comunidad = db.Column(db.String(180), nullable=False)
    
    parroquia = db.relationship('ParroquiaActiva', backref=db.backref('comunidades', lazy='dynamic'))


class NivelActivo(db.Model):
    __tablename__ = 'nivel'
    __table_args__ = {'extend_existing': True}

    id_nivel = db.Column(db.Integer, primary_key=True)
    nombre_nivel = db.Column(db.String(80), nullable=False)
    descripcion = db.Column('descripción ', db.Text, nullable=False)


class ActividadActiva(db.Model):
    __tablename__ = 'actividad'
    __table_args__ = {'extend_existing': True}

    id_actividad = db.Column(db.Integer, primary_key=True)
    fecha_actividad = db.Column(db.Date, nullable=False)
    tipo_actividad = db.Column(db.ARRAY(db.String(20)), nullable=False)
    id_comunidad = db.Column(db.Integer, db.ForeignKey('comunidad.id_comunidad'), nullable=False)
    id_nivel = db.Column(db.Integer, db.ForeignKey('nivel.id_nivel'), nullable=False)

    comunidad = db.relationship('ComunidadActiva', backref=db.backref('actividades', lazy='dynamic'))
    nivel = db.relationship('NivelActivo', backref=db.backref('actividades', lazy='dynamic'))


class SensibilizacionActiva(db.Model):
    __tablename__ = 'sensibilizacion '
    __table_args__ = {'extend_existing': True}

    id_sensibilizacion = db.Column('id_sensivilizacion', db.Integer, primary_key=True)
    nombre_sensivilizacion = db.Column(db.Text, nullable=False)
    id_actividad = db.Column(db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False, unique=True)

    # Se agrega foreign_keys explícito aquí también
    actividad = db.relationship('ActividadActiva', foreign_keys=[id_actividad], backref=db.backref('sensibilizacion', uselist=False))

    @property
    def id(self):
        return self.id_sensibilizacion
  
    @property
    def campana(self):
        return self.nombre_sensivilizacion

    @property
    def territorio(self):
        return getattr(getattr(self.actividad, 'comunidad', None), 'nombre_comunidad', '') or ''

    @property
    def fecha(self):
        return getattr(self.actividad, 'fecha_actividad', None)

    @property
    def vocero(self):
        return ''

    @property
    def alcance(self):
        return 0

    @property
    def estado(self):
        return 'registrada'


# ==========================================
# ALIAS Y PARCHADO DE COMPATIBILIDAD
# ==========================================
Actividad = ActividadActiva
Institucion = InstitucionActiva
Sensibilizacion = SensibilizacionActiva