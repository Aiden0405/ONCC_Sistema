from datetime import datetime
from app import db
from sqlalchemy.orm import synonym

class Actividad(db.Model):
    __tablename__ = 'actividad'
    __table_args__ = {'extend_existing': True}

    # 1. Campos REALES estrictos (Coinciden exactamente con tu \d actividad de Postgres)
    id_actividad = db.Column(db.Integer, primary_key=True)
    fecha_actividad = db.Column(db.Date, nullable=False)
    tipo_actividad = db.Column(db.String(50), nullable=False)
    id_comunidad = db.Column(db.Integer, db.ForeignKey('comunidad.id_comunidad'), nullable=False)
    divulgacion = db.relationship(
        'Divulgacion', 
        back_populates='actividad_obj', 
        uselist=False,
        viewonly=True 
        )
    # 2. Sinónimos reales para soporte de consultas antiguas
    id = synonym('id_actividad')
    fecha = synonym('fecha_actividad')
    actividad = synonym('tipo_actividad')
    creado_en = synonym('fecha_actividad')      
    actualizado_en = synonym('fecha_actividad') 

    # 3. Propiedades virtuales (Evitan que SQLAlchemy las busque en la DB, pero responden si el código las pide)
    @property
    def id_nivel(self):
        return 1  # Retorna un valor por defecto seguro para evitar errores en vistas

    @property
    def id_usuario(self):
        return None

    @property
    def fotos_archivos(self):
        return None

    @property
    def area(self):
        return "Ambiental"

    @property
    def responsable(self):
        return "Técnico ONCC"

    @property
    def estado(self):
        return "Registrada"

    @property
    def estado_geo(self):
        return "Lara"

    @property
    def municipio(self):
        return "Sin municipio"

    @property
    def parroquia(self):
        return "Sin parroquia"

    @property
    def descripcion(self):
        return "Monitoreo institucional"

    @property
    def poblacion(self):
        return 0

    @property
    def acuerdos(self):
        return ""

    @property
    def minuta_archivo(self):
        return None

    def __repr__(self):
        return f"<Actividad {self.tipo_actividad} ({self.id_actividad})>"