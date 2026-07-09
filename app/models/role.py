from app import db
from sqlalchemy.orm import synonym


role_permissions = db.Table(
    'permiso',
    db.Column('id_modulo', db.Integer, db.ForeignKey('modulos.id_modulo')),
    db.Column('id_rol', db.Integer, db.ForeignKey('roles.id_rol')),
)


class Role(db.Model):
    __tablename__ = 'roles'

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(80), unique=True, nullable=False)

    id = synonym('id_rol')
    nombre = synonym('nombre_rol')

    usuarios = db.relationship('Usuario', back_populates='role', primaryjoin="Role.id_rol == foreign(Usuario.id_rol)")
    permissions = db.relationship('Permission', secondary=role_permissions, back_populates='roles')

    def __init__(self, **kwargs):
        nombre = kwargs.pop('nombre', None)
        descripcion = kwargs.pop('descripcion', None)
        super().__init__(**kwargs)
        if nombre is not None:
            self.nombre_rol = nombre
        self._descripcion = descripcion or ''

    @property
    def descripcion(self):
        return self._descripcion or ''

    @descripcion.setter
    def descripcion(self, value):
        self._descripcion = value or ''

    def __repr__(self):
        return f"<Role {self.nombre_rol}>"


class Permission(db.Model):
    __tablename__ = 'modulos'

    id_modulo = db.Column(db.Integer, primary_key=True)
    nombre_modulo = db.Column(db.String(80), unique=True, nullable=False)
    descripcion_modulo = db.Column(db.Text, nullable=False)

    id = synonym('id_modulo')
    nombre = synonym('nombre_modulo')
    descripcion = synonym('descripcion_modulo')

    roles = db.relationship('Role', secondary=role_permissions, back_populates='permissions')

    def __init__(self, **kwargs):
        nombre = kwargs.pop('nombre', None)
        descripcion = kwargs.pop('descripcion', None)
        super().__init__(**kwargs)
        if nombre is not None:
            self.nombre_modulo = nombre
        if descripcion is not None:
            self.descripcion_modulo = descripcion

    def __repr__(self):
        return f"<Permission {self.nombre_modulo}>"
