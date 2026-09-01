from app import db


class Tecnico(db.Model):
    __tablename__ = 'tecnicos'

    id_tecnico = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(15), nullable=False)
    nombres = db.Column(db.String(60), nullable=False)
    apellidos = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"<Tecnico {self.id_tecnico}: {self.nombres} {self.apellidos}>"