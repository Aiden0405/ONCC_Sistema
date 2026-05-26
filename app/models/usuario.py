from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Asociación usuario <-> rol (many-to-many)
user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('usuarios.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
)


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    # Columnas: normalizadas a 'correo' tal como solicita la documentación
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(50), nullable=False, default='Técnico')
    estatus = db.Column(db.Boolean, nullable=False, default=True)

    # Relación con roles
    roles = db.relationship('Role', secondary=user_roles, back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # --- helpers de autorización ---
    def has_role(self, role_name: str) -> bool:
        """Verifica si el usuario tiene el rol indicado.

        - Si `rol` (campo simple) coincide, retorna True.
        - También revisa la relación many-to-many `roles` por nombre.
        """
        if not role_name:
            return False
        rn = role_name.strip().lower()
        try:
            if (self.rol or '').strip().lower() == rn:
                return True
        except Exception:
            pass
        try:
            for r in (self.roles or []):
                if (getattr(r, 'nombre', '') or '').strip().lower() == rn:
                    return True
        except Exception:
            pass
        return False

    def has_permission(self, permission_name: str) -> bool:
        """Verifica si el usuario posee el permiso indicado a través de sus roles."""
        if not permission_name:
            return False
        pn = permission_name.strip().lower()
        try:
            for r in (self.roles or []):
                for p in (getattr(r, 'permissions', []) or []):
                    if (getattr(p, 'nombre', '') or '').strip().lower() == pn:
                        return True
        except Exception:
            pass
        return False

    # Sinónimos para compatibilidad con código antiguo
    from sqlalchemy.orm import synonym
    id_usuario = synonym('id')
    email = synonym('correo')

    def __repr__(self):
        return f"<Usuario {self.correo}>"