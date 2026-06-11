from datetime import datetime

from app import db


class Actividad(db.Model):
    __tablename__ = 'actividades'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(120), nullable=False)
    actividad = db.Column(db.String(180), nullable=False)
    responsable = db.Column(db.String(120), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='Planificada')
    estado_geo = db.Column(db.String(80), nullable=False, default='Lara')
    municipio = db.Column(db.String(120), nullable=False, default='Sin municipio')
    parroquia = db.Column(db.String(120), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    poblacion = db.Column(db.Integer, nullable=False, default=0)
    acuerdos = db.Column(db.Text, nullable=True)
    minuta_archivo = db.Column(db.String(255), nullable=True)
    fotos_archivos = db.Column(db.Text, nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

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