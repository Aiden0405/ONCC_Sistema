from datetime import datetime

from app import db


class BitacoraTransaccion(db.Model):
    __tablename__ = 'bitacora_transacciones'

    id = db.Column(db.Integer, primary_key=True)
    modulo = db.Column(db.String(40), nullable=False)
    registro_id = db.Column(db.Integer, nullable=False)
    accion = db.Column(db.String(60), nullable=False)
    estado_nuevo = db.Column(db.String(20), nullable=True)
    usuario = db.Column(db.String(120), nullable=False)
    detalle = db.Column(db.String(255), nullable=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
