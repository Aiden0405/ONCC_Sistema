from datetime import datetime, timedelta

from app import db
from sqlalchemy.orm import foreign

class PasswordReset(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'password_resets'

    id = db.Column(db.Integer, primary_key=True)
    
    # 1. Mantenemos el ID numérico libre de restricciones físicas cruzadas
    user_id = db.Column(db.Integer, nullable=False)
    
    token = db.Column(db.String(128), unique=True, nullable=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiracion = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(hours=2))
    usado = db.Column(db.Boolean, nullable=False, default=False)

    # 2. CORRECCIÓN DEFINITIVA: Quitamos el lazy='dynamic' en conflicto
    usuario = db.relationship(
        'Usuario', 
        primaryjoin="PasswordReset.user_id == foreign(Usuario.id_usuario)",
        backref='password_resets'
    )

    def is_valid(self):
        return (not self.usado) and (datetime.utcnow() <= self.expiracion)