from datetime import datetime

from app import db


class ReporteTransaccional(db.Model):
    __tablename__ = 'reportes_transaccionales'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    modulo_origen = db.Column(db.String(50), nullable=False)
    rango_desde = db.Column(db.Date, nullable=True)
    rango_hasta = db.Column(db.Date, nullable=True)
    formato = db.Column(db.String(20), nullable=False, default='PDF')
    estado = db.Column(db.String(20), nullable=False, default='borrador')
    responsable = db.Column(db.String(120), nullable=False, default='Analista ONCC')
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
