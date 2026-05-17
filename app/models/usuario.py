from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# UserMixin le da a la clase atributos mágicos como is_authenticated o is_active para Flask-Login
# Asociación usuario <-> rol (many-to-many)
user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('usuarios.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
)


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    # Columnas de la base de datos para PostgreSQL
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(50), nullable=False, default='Técnico')
    estatus = db.Column(db.Boolean, default=True)

    # Relación con roles
    roles = db.relationship('Role', secondary=user_roles, back_populates='users')

    # Función para encriptar la contraseña antes de guardarla en BD
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Función para verificar si la contraseña ingresada en el login coincide con la encriptada
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(r.nombre == role_name for r in (self.roles or []))

    def has_permission(self, permission_name):
        for r in (self.roles or []):
            for p in getattr(r, 'permissions', []):
                if p.nombre == permission_name:
                    return True
        return False