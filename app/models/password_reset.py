from datetime import datetime, timedelta

from app import db


class PasswordReset(db.Model):
    __tablename__ = 'password_resets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(128), unique=True, nullable=False)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiracion = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(hours=2))
    usado = db.Column(db.Boolean, nullable=False, default=False)

    usuario = db.relationship('Usuario', backref=db.backref('password_resets', lazy='dynamic'))

    def is_valid(self):
        return (not self.usado) and (datetime.utcnow() <= self.expiracion)
