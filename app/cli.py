import os
import secrets
from flask import current_app
from app import db
from app.models.usuario import Usuario
from app.models.role import Role, Permission


def register_cli_commands(app):
    @app.cli.command('seed')
    def seed():
        """Seed initial data: roles, permissions and admin user."""
        do_seed()

    @app.cli.command('assign-super-role')
    def assign_super_role_cmd():
        """Crear rol super y asociarlo a usuarios cuyo campo `rol` coincida."""
        assign_super_role()


def do_seed():
    with current_app.app_context():
        # Roles
        super_role_name = current_app.config.get('SUPER_ROLE_NAME', 'Director Regional')
        director_role = Role.query.filter_by(nombre=super_role_name).first()
        if not director_role:
            director_role = Role(nombre=super_role_name, descripcion='Acceso total')
            db.session.add(director_role)

        admin_role = Role.query.filter_by(nombre='Administrador').first()
        if not admin_role:
            admin_role = Role(nombre='Administrador', descripcion='Gestiona usuarios y configuración')
            db.session.add(admin_role)

        tecnico_role = Role.query.filter_by(nombre='Técnico').first()
        if not tecnico_role:
            tecnico_role = Role(nombre='Técnico', descripcion='Operativo de campo')
            db.session.add(tecnico_role)

        # Permisos
        p_manage_users = Permission.query.filter_by(nombre='manage_users').first()
        if not p_manage_users:
            p_manage_users = Permission(nombre='manage_users', descripcion='Crear/Editar/Eliminar usuarios')
            db.session.add(p_manage_users)

        p_manage_roles = Permission.query.filter_by(nombre='manage_roles').first()
        if not p_manage_roles:
            p_manage_roles = Permission(nombre='manage_roles', descripcion='Gestionar roles y permisos')
            db.session.add(p_manage_roles)

        db.session.commit()

        # Asociar permisos
        if p_manage_users not in admin_role.permissions:
            admin_role.permissions.append(p_manage_users)
        if p_manage_roles not in director_role.permissions:
            director_role.permissions.append(p_manage_roles)

        db.session.commit()

        # Crear usuario Director
        director_email = os.environ.get('ADMIN_EMAIL', 'director@oncc.gob.ve')
        director = Usuario.query.filter_by(email=director_email).first()
        if not director:
            pw = os.environ.get('ADMIN_PASSWORD')
            if not pw:
                pw = secrets.token_urlsafe(8)
                print(f'ADMIN_PASSWORD no definido. Se generó: {pw}')

            nuevo = Usuario(nombre=super_role_name, email=director_email, rol=super_role_name, estatus=True)
            nuevo.set_password(pw)
            db.session.add(nuevo)
            db.session.commit()

            # Asignar rol
            nuevo.roles.append(director_role)
            db.session.commit()
            print(f"Usuario '{director_email}' creado con rol {super_role_name}.")
        else:
            print(f'Usuario {director_email} ya existe.')

        print('Seed completado.')


def assign_super_role():
    with current_app.app_context():
        super_role_name = current_app.config.get('SUPER_ROLE_NAME', 'Director Regional')
        role = Role.query.filter_by(nombre=super_role_name).first()
        if not role:
            role = Role(nombre=super_role_name, descripcion='Acceso total (creado automáticamente)')
            db.session.add(role)
            db.session.commit()
            print(f'Rol creado: {super_role_name}')

        users = Usuario.query.filter_by(rol=super_role_name).all()
        if not users:
            print(f'No se encontraron usuarios con campo `rol` = "{super_role_name}"')
            return

        updated = 0
        for u in users:
            if role not in u.roles:
                u.roles.append(role)
                updated += 1
        db.session.commit()
        print(f'Asociado rol {super_role_name} a {updated} usuario(s).')
