from app import db
from sqlalchemy import func, UniqueConstraint

class MapaClimatico(db.Model):
    __tablename__ = 'mapa_climatico'
    
    id_mapa_climatico = db.Column(db.Integer, primary_key=True)
    id_estado = db.Column(db.Integer, db.ForeignKey('estado.id_estado'), nullable=False)
    tipo_de_mapa = db.Column(db.String(50), nullable=False)
    url_mapa = db.Column(db.String(250), nullable=False)
    fecha_creacion = db.Column(db.Date, nullable=False, default=func.current_date())

    # Relación bidireccional con registros climáticos
    registros = db.relationship('RegistroClimatico', backref='mapa_climatico_rel', lazy=True, cascade="all, delete-orphan")


class RegistroClimatico(db.Model):
    __tablename__ = 'registros_climaticos'
    
    # Clave primaria compuesta según el diseño de la base de datos
    id_registro = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    fecha_registro = db.Column(db.Date, primary_key=True, nullable=False)
    
    id_equipo = db.Column(db.Integer, db.ForeignKey('equipo.id_equipo'), nullable=False)
    id_mapa_climatico = db.Column(db.Integer, db.ForeignKey('mapa_climatico.id_mapa_climatico'), nullable=True)
    
    temperatura = db.Column(db.Float, nullable=False)
    precipitaciones = db.Column(db.Float, nullable=False)
    vientos = db.Column(db.Float, nullable=False)
    humedad = db.Column(db.Float, nullable=False)

    __table_args__ = (
        UniqueConstraint('fecha_registro', 'id_equipo', name='registros_climaticos_fecha_registro_id_equipo_key'),
    )