#MODELO
from app import db

class Formacion(db.Model):
    __tablename__ = 'formacion'
    __table_args__ = {'extend_existing': True}

    id_formacion = db.Column(db.Integer, primary_key=True)
    nombre_formacion = db.Column(db.Text, nullable=False)
    id_institucion = db.Column(db.Integer, db.ForeignKey('institucion.id_institucion'), nullable=False)
    id_actividad = db.Column(db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False)


class Institucion(db.Model):
    __tablename__ = 'institucion'
    __table_args__ = {'extend_existing': True}

    id_institucion = db.Column(db.Integer, primary_key=True)
    nombre_institucion = db.Column(db.String(50), nullable=False)
    id_comunidad = db.Column(db.Integer, db.ForeignKey('comunidad.id_comunidad'), nullable=False)
    tipo_institucion = db.Column(db.String(20), nullable=False)
    direccion_exacta = db.Column(db.String(100), nullable=False)
    numero_contacto = db.Column(db.String(25), nullable=False)
    correo_electronico = db.Column(db.String(40), nullable=False)