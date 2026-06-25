from datetime import datetime
from app import db

class MapaRiesgo(db.Model): # Cambiamos el nombre de la clase a MapaRiesgo
    __tablename__ = 'mapa_riesgo'

    # Ajuste de nombre de columna según el backup oficial
    id_mapa_riesgo = db.Column(db.Integer, primary_key=True) 
    
    # Columnas que sí existen en la tabla oficial
    id_actividad = db.Column(db.Integer, nullable=False)
    tipo_actividad = db.Column(db.String(50), default='MAPA_RIESGO', nullable=False)
    ruta_kml = db.Column(db.String(250), nullable=True)
    ruta_imagen_mapa = db.Column(db.String(250), nullable=True)
    
    # Campo con valor por defecto según el backup
    fecha_registro = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    # NOTA: Los campos (nombre, archivo, estado, version, cobertura, responsable, creado_en, actualizado_en)
    # fueron eliminados porque NO existen en la tabla 'mapa_riesgo' del respaldo oficial.