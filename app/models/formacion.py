# MODELO
from app import db
from app.models.esquema_activo import ActividadActiva, InstitucionActiva

class FormacionActiva(db.Model):
    __tablename__ = 'formacion'
    __table_args__ = {'extend_existing': True}

    id_formacion = db.Column(db.Integer, primary_key=True)
    nombre_formacion = db.Column(db.Text, nullable=False)
    id_actividad = db.Column('id_actividad ', db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False, unique=True)
    id_institucion = db.Column(db.Integer, db.ForeignKey('intitucion.id_institucion'), nullable=False)

    actividad = db.relationship('ActividadActiva', foreign_keys=[id_actividad], backref=db.backref('formacion', uselist=False))
    institucion = db.relationship('InstitucionActiva', backref=db.backref('formaciones', lazy='dynamic'))

    @property
    def id(self):
        return self.id_formacion

    @property
    def tema_real(self):
        # Separo el string para sacar solo el tema de la formación, centralizando esta lógica en el modelo
        if "||" in self.nombre_formacion:
            return self.nombre_formacion.split("||", 1)[0]
        return self.nombre_formacion

    @property
    def tecnico_real(self):
        # Extraigo el nombre del técnico de la cadena para no tener que hacerlo en la vista
        if "||" in self.nombre_formacion:
            return self.nombre_formacion.split("||", 1)[1]
        return "No asignado"

    @classmethod
    def obtener_historial_completo(cls):
        # Aquí va la consulta a la base de datos (lógica de datos)
        historial = db.session.query(
            cls, 
            InstitucionActiva, 
            ActividadActiva
        ).join(
            InstitucionActiva, cls.id_institucion == InstitucionActiva.id_institucion
        ).join(
            ActividadActiva, cls.id_actividad == ActividadActiva.id_actividad
        ).order_by(cls.id_formacion.desc()).all()

        formaciones_procesadas = []
        for formacion, institucion, actividad in historial:
            # Formateo la fecha directamente en el modelo
            fecha_lista = actividad.fecha_actividad.strftime('%d/%m/%Y') if actividad.fecha_actividad else 'N/D'
            
            formaciones_procesadas.append({
                'id_formacion': formacion.id_formacion,
                'tema': formacion.tema_real,
                'tecnico': formacion.tecnico_real,
                'nombre_institucion': institucion.nombre_institucion,
                'fecha_actividad_cruda': actividad.fecha_actividad,
                'fecha_formateada': fecha_lista,
                'id_actividad': formacion.id_actividad,
                'id_nivel': actividad.id_nivel,
                'id_institucion': formacion.id_institucion
            })
        return formaciones_procesadas