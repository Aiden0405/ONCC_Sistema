from datetime import datetime

from app import db


class Actividad(db.Model):
    __tablename__ = 'actividades'
    __table_args__ = {'extend_existing': True}

    # 1. Campos REALES estrictos (Coinciden exactamente con tu \d actividad de Postgres)
    id_actividad = db.Column(db.Integer, primary_key=True)
    fecha_actividad = db.Column(db.Date, nullable=False)
    tipo_actividad = db.Column(db.String(50), nullable=False)
    id_comunidad = db.Column(db.Integer, db.ForeignKey('comunidad.id_comunidad'), nullable=False)

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
        return f"<Actividad {self.actividad} ({self.id})>"
    
    # Sinónimos para compatibilidad con código que usa otras denominaciones
    from sqlalchemy.orm import synonym
    id_actividad = synonym('id')
    titulo = synonym('actividad')
    fecha_actividad = synonym('fecha')
    estatus_actividad = synonym('estado')
    created_at = synonym('creado_en')
    updated_at = synonym('actualizado_en')

# class Nivel(db.Model):
#     __tablename__ = 'nivel'
#     __table_args__ = {'extend_existing': True}

#     id_nivel = db.Column(db.Integer, primary_key=True)
#     nombre_nivel = db.Column(db.String(25), nullable=False)
#     descripcion = db.Column('descripción ', db.String(255), nullable=True)

#     def __repr__(self):
#         return f"<Nivel {self.nombre_nivel}>"