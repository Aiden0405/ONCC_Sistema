from datetime import datetime

from app import db


class Formacion(db.Model):
    __tablename__ = 'formaciones'

    id = db.Column(db.Integer, primary_key=True)
    tema = db.Column(db.String(150), nullable=False)
    comunidad = db.Column(db.String(120), nullable=False)
    facilitador = db.Column(db.String(120), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    asistentes = db.Column(db.Integer, nullable=False, default=0)
    estado = db.Column(db.String(20), nullable=False, default='borrador')
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
