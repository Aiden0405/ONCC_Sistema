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
    id_institucion = db.Column(db.Integer, db.ForeignKey('institucion.id_institucion'), nullable=True)
    tipo_actividad = db.Column(db.String(50), nullable=False, default='FORMACION')
    tipo_destino = db.Column(db.String(30), nullable=False, default='COMUNIDAD')
    id_tecnico = db.Column(db.Integer, db.ForeignKey('tecnicos.id_tecnico'), nullable=True)
    id_nivel = db.Column(db.Integer, db.ForeignKey('nivel.id_nivel'), nullable=False)

    # 🌟 Nombres de backref únicos para no colisionar con Actividad
    actividad = db.relationship(
        'Actividad', 
        foreign_keys=[id_actividad], 
        backref=db.backref('formacion_activa_rel', uselist=False, cascade="all, delete-orphan")
    )
    institucion = db.relationship('InstitucionActiva', backref=db.backref('formaciones', lazy='dynamic'))
    tecnico = db.relationship('Tecnico', backref=db.backref('formaciones', lazy='dynamic'))

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
    def obtener_historial_completo(cls, tipo_actividad=None):
        historial = db.session.query(
            cls, 
            InstitucionActiva,
            ComunidadActiva,
            NivelActivo,
            Actividad
        ).join(
            Actividad,
            (cls.id_actividad == Actividad.id_actividad)
        ).outerjoin(
            InstitucionActiva, cls.id_institucion == InstitucionActiva.id_institucion
        ).join(
            ComunidadActiva, Actividad.id_comunidad == ComunidadActiva.id_comunidad
        ).join(
            NivelActivo, cls.id_nivel == NivelActivo.id_nivel
        )
        if tipo_actividad:
            historial = historial.filter(cls.tipo_actividad == tipo_actividad)
        historial = historial.order_by(cls.id_formacion.desc()).all()

        formaciones_procesadas = []
        for formacion, institucion, comunidad, nivel, actividad in historial:
            fecha_lista = actividad.fecha_actividad.strftime('%d/%m/%Y') if actividad.fecha_actividad else 'N/D'
            
            formaciones_procesadas.append({
                'id_formacion': formacion.id_formacion,
                'id_sensibilizacion': formacion.id_formacion,
                'tema': formacion.tema_real,
                'campana': formacion.tema_real,
                'tecnico': formacion.tecnico_real,
                'facilitador': formacion.tecnico_real,
                'nombre_institucion': institucion.nombre_institucion if institucion else None,
                'tipo': formacion.tipo_actividad,
                'tipo_destino': formacion.tipo_destino,
                'nombre_comunidad': comunidad.nombre_comunidad,
                'nombre_nivel': nivel.nombre_nivel,
                'id_tecnico': formacion.id_tecnico,
                'fecha_actividad_cruda': actividad.fecha_actividad,
                'fecha_formateada': fecha_lista,
                'id_actividad': formacion.id_actividad,
                'id_comunidad': actividad.id_comunidad,
                'id_nivel': formacion.id_nivel or actividad.id_nivel,
                'id_institucion': formacion.id_institucion
            })
        return formaciones_procesadas


    @property
    def nombre_sensibilizacion(self):
        return self.nombre_formacion

    @property
    def campana_real(self):
        return self.tema_real

    @property
    def facilitador_real(self):
        return self.tecnico_real

