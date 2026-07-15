from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db
from geoalchemy2 import Geometry

class MapaRiesgo(db.Model):
    __tablename__ = 'mapa_riesgo'

    id_mapa_riesgo = db.Column(db.Integer, primary_key=True)
    id_actividad = db.Column(db.Integer, nullable=False)
    tipo_actividad = db.Column(db.String(50), nullable=False, default='MAPA_RIESGO')
    
    ruta_kml = db.Column(db.String(250), nullable=True)
    ruta_imagen_mapa = db.Column(db.String(250), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    nombre = db.Column(db.String, nullable=True)

    # Restricción explícita de llave foránea compuesta hacia actividad
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['id_actividad', 'tipo_actividad'],
            ['actividad.id_actividad', 'actividad.tipo_actividad'],
            name='mapa_riesgo_actividad_compuesta_fkey',
            onupdate='CASCADE', ondelete='RESTRICT'
        ),
    )

    # Relación con elementos espacializados (PostGIS)
    elementos = db.relationship('ElementoMapaRiesgo', backref='mapa_asociado', cascade='all, delete-orphan')

class ElementoMapaRiesgo(db.Model):
    __tablename__ = 'elemento_mapa_riesgo'

    id_elemento = db.Column(db.Integer, primary_key=True)
    id_mapa_riesgo = db.Column(db.Integer, db.ForeignKey('mapa_riesgo.id_mapa_riesgo', ondelete='CASCADE'), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    subcategoria = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    
    # Campo geométrico
    geometria = db.Column(Geometry(geometry_type='GEOMETRY', srid=4326), nullable=False)