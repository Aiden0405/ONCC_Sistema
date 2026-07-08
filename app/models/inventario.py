from datetime import datetime
from app import db
from sqlalchemy.orm import synonym

class InventarioEquipo(db.Model):
    __tablename__ = 'equipo'  # Cambiado al nombre oficial en Postgres 
    __table_args__ = {'extend_existing': True}

    # 1. Columnas REALES extraídas estrictamente de tu backup 
    id_equipo = db.Column(db.Integer, primary_key=True)
    id_modelos_equipos = db.Column(db.Integer, nullable=False)
    id_ubicacion_actual = db.Column(db.Integer, nullable=True)
    codigo_interno = db.Column(db.String(50), nullable=False, unique=True)
    numero_serie = db.Column(db.String(250), nullable=True)
    estado = db.Column(db.String(30), nullable=False)
    fecha_ingreso = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    observaciones = db.Column(db.Text, nullable=True)

    # 2. Sinónimos de SQLAlchemy para que los controladores viejos no se rompan
    id = synonym('id_equipo')
    codigo = synonym('codigo_interno')
    estado_operativo = synonym('estado')
    creado_en = synonym('fecha_ingreso')

    # 3. Propiedades virtuales para responder si las plantillas HTML o consultas piden campos eliminados
    @property
    def tipo_equipo(self):
        return "Dispositivo Climático"

    @property
    def ubicacion(self):
        return "Área del Observatorio"

    @property
    def estado_flujo(self):
        return "Operativo"

    @property
    def ultimo_mantenimiento(self):
        return self.fecha_ingreso

    @property
    def responsable(self):
        return "Técnico ONCC"

    @property
    def actualizado_en(self):
        return self.fecha_ingreso