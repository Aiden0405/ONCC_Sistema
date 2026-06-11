# Autor: Gabriel Castañeda
from datetime import datetime
from app import db

class MapaRegistro(db.Model):
    __tablename__ = 'mapas_registro'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    tipo_mapa = db.Column(db.String(40), nullable=False)  # riesgo, temperatura, precipitacion
    archivo = db.Column(db.String(255), nullable=True)
    estado = db.Column(db.String(20), nullable=False, default='borrador')
    version = db.Column(db.String(30), nullable=False, default='v1.0')
    cobertura = db.Column(db.String(120), nullable=False, default='Regional')
    responsable = db.Column(db.String(120), nullable=False)
    id_parroquia = db.Column(db.Integer, db.ForeignKey('parroquia.id_parroquia'), nullable=True) # ¡Agregado según tu SQL!
    
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)