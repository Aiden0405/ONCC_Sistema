from datetime import datetime
from app import db
from sqlalchemy.orm import synonym

class Notificacion(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'notificaciones'

    id_notificacion = db.Column(db.BigInteger, primary_key=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False, default='Sistema')
    mensaje = db.Column(db.Text, nullable=False)
    leido = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Alias para compatibilidad con código que use usuario_id
    usuario_id = synonym('id_usuario')

    usuario = db.relationship(
        'Usuario', 
        primaryjoin="Notificacion.id_usuario == Usuario.id_usuario",
        foreign_keys=[id_usuario],
        backref='notificaciones_asociadas'
    )