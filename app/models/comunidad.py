from app import db

class Comunidad(db.Model):
    __tablename__ = 'comunidad'
    __table_args__ = {'extend_existing': True}
    id_comunidad = db.Column(db.Integer, primary_key=True)
    nombre_comunidad = db.Column(db.String(50), nullable=False)
    id_parroquia = db.Column(db.Integer, db.ForeignKey('parroquia.id_parroquia'), nullable=False)