from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from sqlalchemy.orm import synonym

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(30), nullable=False)
    clave_usuario = db.Column('clave usuario', db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)
    
    # 1. AGREGADOS: Columnas esenciales que pide tu controlador y tu base de datos
    # (Nota: Si en tu Postgres la columna se llama 'correo_usuario', cambia el nombre aquí)
    correo = db.Column(db.String(100), nullable=True) 
    estatus = db.Column(db.Boolean, default=True)

    id = synonym('id_usuario')
    nombre = synonym('nombre_usuario')

    role = db.relationship('Role', back_populates='usuarios')

    # 2. SOLUCIÓN PARA EL HTML: Mapea automáticamente {{ usuario.rol }} al nombre del rol real
    @property
    def rol(self):
        return self.role.nombre if self.role else 'Sin Rol'

    def has_role(self, *role_names):
        if not self.role:
            return False
        return self.role.nombre in role_names or self.role.nombre_rol in role_names

    def set_password(self, password):
        self.clave_usuario = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.clave_usuario, password)

    def get_id(self):
        return str(self.id_usuario)