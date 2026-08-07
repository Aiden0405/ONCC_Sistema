from app import db
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy import func, ForeignKeyConstraint, UniqueConstraint



class Simbologia(db.Model):
    __tablename__ = 'catalogo_simbologia'
    
    id_simbologia = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(50), nullable=False)    # Ej: "Riesgo", "Recurso", "Vulnerabilidad"
    nombre_elemento = db.Column(db.String(100), nullable=False) # Ej: "Ambulatorio", "Inundación", "Vialidad"
    
    # Restricción espacial: ¿Este elemento se dibuja como Punto, Línea o Polígono?
    tipo_geometria = db.Column(db.String(20), nullable=False) 
    
    # EL CORAZÓN DE LEAFLET: Aquí guardas el JSON con el diseño nativo
    # Para polígonos: {"color": "#ff0000", "fillOpacity": 0.5}
    # Para marcadores: {"isIcon": true, "iconUrl": "/static/img/ambulatorio.png", "iconSize": [30, 30]}
    estilo_defecto = db.Column(JSONB, nullable=False)



class MapaRiesgo(db.Model):
    __tablename__ = 'mapas_riesgo'
    
    id_mapa_riesgo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(150), nullable=False)
    fecha_creacion = db.Column(db.DateTime(timezone=True), server_default=func.now())
    poligonal_comunidad = db.Column(Geometry(geometry_type='GEOMETRY', srid=4326), nullable=True)
    ruta_imagen_mapa = db.Column(db.String(255), nullable=True)
    ruta_kml = db.Column(db.String(255), nullable=True)
    
    # SOLUCIÓN 3: AQUÍ SE GUARDA EL LAYOUT
    # Guardará las coordenadas como JSON: [[lat_sw, lng_sw], [lat_ne, lng_ne]]
    limites_layout = db.Column(JSONB, nullable=True) 

    id_actividad = db.Column(db.Integer, nullable=False)
    tipo_actividad = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    
    __table_args__ = (
        ForeignKeyConstraint(
            ['id_actividad', 'tipo_actividad'], 
            ['actividad.id_actividad', 'actividad.tipo_actividad'],
            name='fk_mapas_riesgo_actividad'
        ),
        UniqueConstraint('id_actividad', 'tipo_actividad', name='uq_mapas_riesgo_actividad')
    )
    
    elementos = db.relationship('ElementosMapaRiesgo', backref='mapa', cascade="all, delete-orphan")


class ElementosMapaRiesgo(db.Model):
    __tablename__ = 'elementos_mapariesgo'
    
    id_elemento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_mapa_riesgo = db.Column(db.Integer, db.ForeignKey('mapas_riesgo.id_mapa_riesgo'), nullable=False)
    id_simbologia = db.Column(db.Integer, db.ForeignKey('catalogo_simbologia.id_simbologia'), nullable=False)
    
    # SOLUCIÓN 2: COLUMNA FALTANTE PARA EL NOMBRE PROPIO
    nombre_propio = db.Column(db.String(150), nullable=True)
    
    descripcion_especifica = db.Column(db.Text, nullable=True)
    estilo_personalizado = db.Column(JSONB, nullable=True) 
    geom = db.Column(Geometry(geometry_type='GEOMETRY', srid=4326), nullable=False)
   