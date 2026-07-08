# MODELO 
from app import db
from app.models.esquema_activo import ActividadActiva, ComunidadActiva

class SensibilizacionActiva(db.Model):
    __tablename__ = 'sensibilizacion '
    __table_args__ = {'extend_existing': True}

    id_sensibilizacion = db.Column('id_sensivilizacion', db.Integer, primary_key=True)
    nombre_sensivilizacion = db.Column(db.Text, nullable=False)
    id_actividad = db.Column(db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False, unique=True)

    # Relación directa con la tabla padre 'actividad'
    actividad = db.relationship('ActividadActiva', foreign_keys=[id_actividad], backref=db.backref('sensibilizacion_rel', uselist=False))

    @property
    def id(self):
        return self.id_sensibilizacion
  
    @property
    def campana_real(self):
        # Separo el string para sacar solo el tema o campaña, centralizando la lógica aquí
        if "||" in self.nombre_sensivilizacion:
            return self.nombre_sensivilizacion.split("||", 1)[0]
        return self.nombre_sensivilizacion

    @property
    def facilitador_real(self):
        # Extraigo el nombre del técnico/facilitador de la cadena para no hacerlo en el controlador
        if "||" in self.nombre_sensivilizacion:
            return self.nombre_sensivilizacion.split("||", 1)[1]
        return "No asignado"

    @classmethod
    def obtener_historial_completo(cls):
        # MUDANZA DE CONSULTA: Toda la lógica de datos con JOINs se ejecuta desde aquí
        historial = db.session.query(
            cls,
            ActividadActiva,
            ComunidadActiva
        ).join(
            ActividadActiva, cls.id_actividad == ActividadActiva.id_actividad
        ).join(
            ComunidadActiva, ActividadActiva.id_comunidad == ComunidadActiva.id_comunidad
        ).order_by(cls.id_sensibilizacion.desc()).all()

        sensibilizaciones_procesadas = []
        for sensibilizacion, actividad, comunidad in historial:
            # Procesamos la lista estructurada mapeando las propiedades limpias
            sensibilizaciones_procesadas.append({
                'id_sensibilizacion': sensibilizacion.id_sensibilizacion,
                'campana': sensibilizacion.campana_real,
                'facilitador': sensibilizacion.facilitador_real,
                'nombre_comunidad': comunidad.nombre_comunidad,
                'fecha_actividad': actividad.fecha_actividad,
                'id_actividad': sensibilizacion.id_actividad,
                'id_nivel': actividad.id_nivel,
                'id_comunidad': actividad.id_comunidad
            })
        return sensibilizaciones_procesadas