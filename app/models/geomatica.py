# Autor: Gabriel Castañeda
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from app import db

# 1. TABLA PRINCIPAL: Metadatos del Mapa (Vinculada a Actividades)
class MapaRiesgo(db.Model):
    __tablename__ = 'mapa_riesgo'

    id_mapa_riesgo = db.Column(db.Integer, primary_key=True)
    id_actividad = db.Column(db.Integer, nullable=False)
    
    # Restricción CHECK de la base de datos exige que esto sea siempre 'MAPA_RIESGO'
    tipo_actividad = db.Column(db.String(50), nullable=False, default='MAPA_RIESGO')
    
    ruta_kml = db.Column(db.String(250), nullable=True)
    ruta_imagen_mapa = db.Column(db.String(250), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)

    # Relación para acceder a los polígonos asociados a este mapa fácilmente
    elementos = db.relationship('ElementoMapaRiesgo', backref='mapa_asociado', cascade='all, delete-orphan')

    def __init__(self, id_actividad, descripcion, ruta_kml=None, ruta_imagen_mapa=None, tipo_actividad='MAPA_RIESGO'):
        self.id_actividad = id_actividad
        self.descripcion = descripcion
        self.ruta_kml = ruta_kml
        self.ruta_imagen_mapa = ruta_imagen_mapa
        self.tipo_actividad = tipo_actividad


# 2. TABLA SECUNDARIA: Datos Espaciales (PostGIS)
class ElementoMapaRiesgo(db.Model):
    __tablename__ = 'elemento_mapa_riesgo'

    id_elemento = db.Column(db.Integer, primary_key=True)
    id_mapa_riesgo = db.Column(db.Integer, db.ForeignKey('mapa_riesgo.id_mapa_riesgo', ondelete='CASCADE'), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    subcategoria = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    
    # Aquí es donde realmente se almacena el GeoJSON/Geometría
    geometria = db.Column(Geometry(geometry_type='GEOMETRY', srid=4326), nullable=False)

    def __init__(self, id_mapa_riesgo, categoria, subcategoria, geometria, descripcion=None):
        self.id_mapa_riesgo = id_mapa_riesgo
        self.categoria = categoria
        self.subcategoria = subcategoria
        self.geometria = geometria
        self.descripcion = descripcion