#MODELO
from app import db

class Formacion(db.Model):
    __tablename__ = 'formacion'
    __table_args__ = {'extend_existing': True}

    id_formacion = db.Column(db.Integer, primary_key=True)
    nombre_formacion = db.Column(db.Text, nullable=False)
    id_institucion = db.Column(db.Integer, db.ForeignKey('intitucion.id_institucion'), nullable=False)
    id_actividad = db.Column('id_actividad ', db.Integer, db.ForeignKey('actividad.id_actividad'), nullable=False)


class Institucion(db.Model):
    __tablename__ = 'intitucion'
    __table_args__ = {'extend_existing': True}

    id_institucion = db.Column(db.Integer, primary_key=True)
    nombre_institucion = db.Column(db.String(50), nullable=False)
    id_comunidad = db.Column(db.Integer, db.ForeignKey('comunidad.id_comunidad'), nullable=False)