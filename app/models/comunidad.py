from datetime import datetime

from app import db


class Comunidad(db.Model):
	__tablename__ = 'comunidades'

	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(180), nullable=False)
	vocero = db.Column(db.String(120), nullable=True)
	telefono = db.Column(db.String(40), nullable=True)
	estado = db.Column(db.String(80), nullable=False)
	municipio = db.Column(db.String(120), nullable=False)
	parroquia = db.Column(db.String(120), nullable=True)
	familias = db.Column(db.Integer, nullable=False, default=0)
	fase = db.Column(db.String(60), nullable=False, default='Diagnóstico / Acercamiento')
	fecha_proximo = db.Column(db.Date, nullable=True)
	creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
