from app import db
from datetime import datetime

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=True) # 👈 Queda como entero normal en la BD
    categoria = db.Column(db.String(50), nullable=False, default='Sistema') 
    mensaje = db.Column(db.Text, nullable=False)
    leido = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # 🌟 SOLUCIÓN: Le explicamos a SQLAlchemy cómo unirse usando primaryjoin
    usuario = db.relationship(
        'Usuario', 
        primaryjoin="Notificacion.usuario_id == Usuario.id", # Enlace lógico manual
        foreign_keys=[usuario_id],
        backref='notificaciones_asociadas'
    )