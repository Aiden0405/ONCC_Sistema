from datetime import datetime

from app import db


class VisitaPortal(db.Model):
    __tablename__ = 'visitas_portal'

    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.String(7), nullable=False, index=True)
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
