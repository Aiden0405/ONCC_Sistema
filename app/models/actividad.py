from datetime import datetime

from sqlalchemy.orm import synonym

from app import db


class Actividad(db.Model):
    __tablename__ = 'actividad'
    __table_args__ = {'extend_existing': True}

    id_actividad = db.Column(db.Integer, primary_key=True)
    fecha_actividad = db.Column(db.Date, nullable=False)
    tipo_actividad = db.Column(db.String(50), nullable=False)
    id_comunidad = db.Column(db.Integer, db.ForeignKey('comunidad.id_comunidad'), nullable=False)
    id_nivel = db.Column(db.Integer, db.ForeignKey('nivel.id_nivel'), nullable=True)

    divulgacion = db.relationship(
        'Divulgacion', 
        back_populates='actividad_obj', 
        uselist=False,
        viewonly=True 
    )

    id = synonym('id_actividad')
    fecha = synonym('fecha_actividad')
    actividad = synonym('tipo_actividad')

    def __repr__(self):
        return f"<Actividad {self.tipo_actividad} ({self.id_actividad})>"


class ActividadLegacy(db.Model):
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
        return f"<ActividadLegacy {self.actividad} ({self.id})>"
