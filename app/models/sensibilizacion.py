from datetime import datetime

from app import db


class Sensibilizacion(db.Model):
    __tablename__ = 'sensibilizaciones'

    id = db.Column(db.Integer, primary_key=True)
    campana = db.Column(db.String(150), nullable=False)
    territorio = db.Column(db.String(120), nullable=False)
    vocero = db.Column(db.String(120), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    alcance = db.Column(db.Integer, nullable=False, default=0)
    estado = db.Column(db.String(20), nullable=False, default='borrador')
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
