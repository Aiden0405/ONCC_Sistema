from datetime import datetime

from sqlalchemy.orm import synonym

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
	responsable = db.Column(db.String(120), nullable=False, default='Equipo Geomatica')
	creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class MapaRiesgo(db.Model):
	__tablename__ = 'mapa_riesgo'

	id_mapa_riesgo = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(150), nullable=False, default='')
	descripcion = db.Column(db.Text, nullable=True)
	archivo = db.Column(db.String(255), nullable=True)
	estado = db.Column(db.String(20), nullable=False, default='borrador')
	version = db.Column(db.String(30), nullable=False, default='v1.0')
	cobertura = db.Column(db.String(120), nullable=False, default='Regional')
	responsable = db.Column(db.String(120), nullable=False, default='Equipo Geomatica')
	creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

	id = synonym('id_mapa_riesgo')

