from app import db
from sqlalchemy.orm import synonym, foreign, remote

class Permiso(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'permisos'
    
    id_modulo = db.Column(db.Integer, primary_key=True)
    id_rol = db.Column(db.Integer, primary_key=True)


class Role(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'rol'

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(80), unique=True, nullable=False)

    id = synonym('id_rol')
    nombre = synonym('nombre_rol')

    # Propiedad estática decorativa para evitar que Jinja se queje al leer r.descripcion
    @property
    def descripcion(self):
        return '-'

    # Relación en espejo con Usuario
    usuarios = db.relationship(
        'Usuario', 
        back_populates='role',
        primaryjoin="Role.id_rol == foreign(Usuario.id_rol)"
    )
    
    # Relación directa hacia la tabla pívot de permisos con dirección clara
    permissions_rel = db.relationship(
        'Permiso',
        primaryjoin="Role.id_rol == foreign(remote(Permiso.id_rol))",
        backref='role_obj',
        cascade="all, delete-orphan" 
    )

    # Busca los módulos asociados de forma segura para la plantilla permisos.html
    @property
    def permissions(self):
        modulos_ids = [p.id_modulo for p in self.permissions_rel]
        if not modulos_ids:
            return []
        return Permission.query.filter(Permission.id_modulo.in_(modulos_ids)).all()

    def __init__(self, **kwargs):
        nombre = kwargs.pop('nombre', None)
        kwargs.pop('descripcion', None) # Consumimos el argumento por seguridad
        super().__init__(**kwargs)
        if nombre is not None:
            self.nombre_rol = nombre

    def __repr__(self):
        return f"<Role {self.nombre_rol}>"


class Permission(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'modulos'

    id_modulo = db.Column(db.Integer, primary_key=True)
    nombre_modulo = db.Column(db.String(80), unique=True, nullable=False)
    descripcion_modulo = db.Column(db.Text, nullable=True) 

    id = synonym('id_modulo')
    nombre = synonym('nombre_modulo')
    descripcion = synonym('descripcion_modulo')

    # Relación con la tabla pívot
    roles_rel = db.relationship(
        'Permiso',
        primaryjoin="Permission.id_modulo == foreign(remote(Permiso.id_modulo))",
        backref='permission_obj',
        cascade="all, delete-orphan"
    )

    @property
    def roles(self):
        roles_ids = [r.id_rol for r in self.roles_rel]
        if not roles_ids:
            return []
        return Role.query.filter(Role.id_rol.in_(roles_ids)).all()

    # 🌟 AQUÍ QUEDÓ ACTUALIZADO EL CONSTRUCTOR PARA CAPTURAR EL ID DINÁMICO
    def __init__(self, **kwargs):
        id_modulo = kwargs.pop('id_modulo', None)
        nombre = kwargs.pop('nombre', None)
        descripcion = kwargs.pop('descripcion', None)
        super().__init__(**kwargs)
        
        if id_modulo is not None:
            self.id_modulo = id_modulo
        if nombre is not None:
            self.nombre_modulo = nombre
        if descripcion is not None:
            self.descripcion_modulo = descripcion

    def __repr__(self):
        return f"<Permission {self.nombre_modulo}>"