from app import db
from app.models.actividad import Actividad
class EstadoActivo(db.Model):
    __tablename__ = 'estado'
    __table_args__ = {'extend_existing': True}

    id_estado = db.Column(db.Integer, primary_key=True)
    nombre_estado = db.Column(db.String(80), unique=True, nullable=False)


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
    nombre_nivel = db.Column(db.String(80), unique=True, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)


class InstitucionActiva(db.Model):
    __tablename__ = 'institucion'
    __table_args__ = {'extend_existing': True}

    id_institucion = db.Column(db.Integer, primary_key=True)
    id_comunidad = db.Column(db.Integer, db.ForeignKey('comunidad.id_comunidad'), nullable=False)
    nombre_institucion = db.Column(db.String(100), nullable=False)
    tipo_institucion = db.Column(db.String(50), nullable=False)
    direccion_exacta = db.Column(db.String(250), nullable=False)
    numero_contacto = db.Column(db.String(25), nullable=False)
    correo_electronico = db.Column(db.String(100), nullable=False)

    comunidad = db.relationship('ComunidadActiva', backref=db.backref('instituciones', lazy='dynamic'))


# =========================================================================
# MODELOS COMUNITARIOS
# =========================================================================

class FormacionActiva(db.Model):
    __tablename__ = 'formacion'
    __table_args__ = {'extend_existing': True}

    id_formacion = db.Column(db.Integer, primary_key=True)
    nombre_formacion = db.Column(db.Text, nullable=False)
    id_actividad = db.Column('id_actividad', db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False, unique=True)
    id_institucion = db.Column(db.Integer, db.ForeignKey('institucion.id_institucion'), nullable=False)
    tipo_actividad = db.Column(db.String(50), nullable=False, default='FORMACION')
    id_nivel = db.Column(db.Integer, db.ForeignKey('nivel.id_nivel'), nullable=False)

    # 🌟 Nombres de backref únicos para no colisionar con Actividad
    actividad = db.relationship(
        'Actividad', 
        foreign_keys=[id_actividad], 
        backref=db.backref('formacion_activa_rel', uselist=False, cascade="all, delete-orphan")
    )
    institucion = db.relationship('InstitucionActiva', backref=db.backref('formaciones', lazy='dynamic'))

    @property
    def id(self):
        return self.id_formacion

    @property
    def tema_real(self):
        if "||" in self.nombre_formacion:
            return self.nombre_formacion.split("||", 1)[0]
        return self.nombre_formacion

    @property
    def tecnico_real(self):
        if "||" in self.nombre_formacion:
            return self.nombre_formacion.split("||", 1)[1]
        return "No asignado"

    @classmethod
    def obtener_historial_completo(cls):
        historial = db.session.query(
            cls, 
            InstitucionActiva, 
            Actividad
        ).join(
            InstitucionActiva, cls.id_institucion == InstitucionActiva.id_institucion
        ).join(
            Actividad, cls.id_actividad == Actividad.id_actividad
        ).order_by(cls.id_formacion.desc()).all()

        formaciones_procesadas = []
        for formacion, institucion, actividad in historial:
            fecha_lista = actividad.fecha_actividad.strftime('%d/%m/%Y') if actividad.fecha_actividad else 'N/D'
            
            formaciones_procesadas.append({
                'id_formacion': formacion.id_formacion,
                'tema': formacion.tema_real,
                'tecnico': formacion.tecnico_real,
                'nombre_institucion': institucion.nombre_institucion,
                'fecha_actividad_cruda': actividad.fecha_actividad,
                'fecha_formateada': fecha_lista,
                'id_actividad': formacion.id_actividad,
                'id_comunidad': actividad.id_comunidad,
                'id_nivel': formacion.id_nivel or actividad.id_nivel,
                'id_institucion': formacion.id_institucion
            })
        return formaciones_procesadas


class SensibilizacionActiva(db.Model):
    __tablename__ = 'sensibilizacion'
    __table_args__ = {'extend_existing': True}

    id_sensibilizacion = db.Column('id_sensibilizacion', db.Integer, primary_key=True)
    nombre_sensivilizacion = db.Column('nombre_sensibilizacion', db.Text, nullable=False)
    id_actividad = db.Column(db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False, unique=True)
    tipo_actividad = db.Column(db.String(50), nullable=False, default='SENSIBILIZACION')
    id_nivel = db.Column(db.Integer, db.ForeignKey('nivel.id_nivel'), nullable=False)

    # 🌟 Nombres de backref únicos para no colisionar con Actividad
    actividad = db.relationship(
        'Actividad', 
        foreign_keys=[id_actividad], 
        backref=db.backref('sensibilizacion_activa_rel', uselist=False, cascade="all, delete-orphan")
    )

    @property
    def id(self):
        return self.id_sensibilizacion

    @property
    def nombre_sensibilizacion(self):
        return self.nombre_sensivilizacion

    @nombre_sensibilizacion.setter
    def nombre_sensibilizacion(self, value):
        self.nombre_sensivilizacion = value
  
    @property
    def campana_real(self):
        if "||" in self.nombre_sensibilizacion:
            return self.nombre_sensibilizacion.split("||", 1)[0]
        return self.nombre_sensibilizacion

    @property
    def facilitador_real(self):
        if "||" in self.nombre_sensibilizacion:
            return self.nombre_sensibilizacion.split("||", 1)[1]
        return "No asignado"

    @classmethod
    def obtener_historial_completo(cls):
        historial = db.session.query(
            cls,
            Actividad,
            ComunidadActiva
        ).join(
            Actividad, cls.id_actividad == Actividad.id_actividad
        ).join(
            ComunidadActiva, Actividad.id_comunidad == ComunidadActiva.id_comunidad
        ).order_by(cls.id_sensibilizacion.desc()).all()

        sensibilizaciones_procesadas = []
        for sensibilizacion, actividad, comunidad in historial:
            sensibilizaciones_procesadas.append({
                'id_sensibilizacion': sensibilizacion.id_sensibilizacion,
                'campana': sensibilizacion.campana_real,
                'facilitador': sensibilizacion.facilitador_real,
                'nombre_comunidad': comunidad.nombre_comunidad,
                'fecha_actividad': actividad.fecha_actividad,
                'id_actividad': sensibilizacion.id_actividad,
                'id_nivel': sensibilizacion.id_nivel or actividad.id_nivel,
                'id_comunidad': actividad.id_comunidad
            })
        return sensibilizaciones_procesadas