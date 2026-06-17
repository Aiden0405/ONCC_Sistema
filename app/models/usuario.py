from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from sqlalchemy.orm import synonym, foreign

class Usuario(UserMixin, db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'usuario'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(30), nullable=False)
    correo = db.Column(db.String(50), nullable=False)
    clave = db.Column(db.String(250), nullable=False)
    id_rol = db.Column(db.Integer, nullable=False)
    estatus = db.Column(db.Boolean, default=True)

    id = synonym('id_usuario')
    nombre = synonym('nombre_usuario')

    # Relación lógica directa indicando que trae UN SOLO rol (uselist=False)
    role = db.relationship(
        'Role', 
        back_populates='usuarios', 
        primaryjoin="Role.id_rol == foreign(Usuario.id_rol)",
        uselist=False
    )

    @property
    def rol(self):
        return self.role.nombre_rol if self.role else 'Sin Rol'

    def has_role(self, *role_names):
        if not self.role:
            return False
        return self.role.nombre_rol in role_names

    def set_password(self, password):
        self.clave = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.clave, password)

    def get_id(self):
        return str(self.id_usuario)