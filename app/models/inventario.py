from datetime import datetime

from app import db


class InventarioEquipo(db.Model):
	__tablename__ = 'inventario_equipos'

	id = db.Column(db.Integer, primary_key=True)
	tipo_equipo = db.Column(db.String(120), nullable=False)
	codigo = db.Column(db.String(50), nullable=False, unique=True)
	ubicacion = db.Column(db.String(150), nullable=False)
	estado_operativo = db.Column(db.String(60), nullable=False, default='Operativo')
	estado_flujo = db.Column(db.String(20), nullable=False, default='borrador')
	ultimo_mantenimiento = db.Column(db.Date, nullable=True)
	responsable = db.Column(db.String(120), nullable=False, default='Sin asignar')
	creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

