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

        # Permisos canónicos usados por controladores y plantillas
        permisos_base = [
            ('gestionar_usuarios', 'Crear, editar y eliminar usuarios, roles y accesos'),
            ('gestionar_monitoreo', 'Administrar actividades y monitoreo'),
            ('gestionar_formaciones', 'Administrar formaciones comunitarias'),
            ('gestionar_sensibilizaciones', 'Administrar sensibilizaciones comunitarias'),
            ('crear_divulgaciones', 'Crear contenido de divulgación'),
            ('aprobar_divulgaciones', 'Aprobar y publicar contenido de divulgación'),
        ]

        permisos_creados = {}
        for nombre_permiso, descripcion_permiso in permisos_base:
            permiso = Permission.query.filter_by(nombre=nombre_permiso).first()
            if not permiso:
                permiso = Permission(nombre=nombre_permiso, descripcion=descripcion_permiso)
                db.session.add(permiso)
            permisos_creados[nombre_permiso] = permiso

        db.session.commit()

        # Asociar permisos a roles base
        for permiso_nombre in ('gestionar_usuarios', 'gestionar_monitoreo', 'gestionar_formaciones', 'gestionar_sensibilizaciones', 'crear_divulgaciones'):
            permiso = permisos_creados[permiso_nombre]
            if permiso not in admin_role.permissions:
                admin_role.permissions.append(permiso)

        for permiso_nombre in ('gestionar_usuarios', 'gestionar_monitoreo', 'gestionar_formaciones', 'gestionar_sensibilizaciones', 'crear_divulgaciones', 'aprobar_divulgaciones'):
            permiso = permisos_creados[permiso_nombre]
            if permiso not in director_role.permissions:
                director_role.permissions.append(permiso)

        # Compatibilidad con permisos legados si ya existen en BD
        legacy_permissions = {
            'manage_users': 'gestionar_usuarios',
            'manage_roles': 'gestionar_usuarios',
        }
        for legacy_name, canonical_name in legacy_permissions.items():
            legacy_perm = Permission.query.filter_by(nombre=legacy_name).first()
            canonical_perm = permisos_creados[canonical_name]
            if legacy_perm and legacy_perm not in admin_role.permissions:
                admin_role.permissions.append(legacy_perm)
            if legacy_perm and legacy_perm not in director_role.permissions:
                director_role.permissions.append(legacy_perm)

        db.session.commit()

        # Crear usuario Director
        director_email = os.environ.get('ADMIN_EMAIL', 'director@oncc.gob.ve')
        director = Usuario.query.filter_by(correo=director_email).first()
        if not director:
            pw = os.environ.get('ADMIN_PASSWORD')
            if not pw:
                pw = secrets.token_urlsafe(8)
                print(f'ADMIN_PASSWORD no definido. Se generó: {pw}')

            nuevo = Usuario(nombre=super_role_name, correo=director_email, id_rol=director_role.id_rol, estatus=True)
            nuevo.set_password(pw)
            db.session.add(nuevo)
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

        users = Usuario.query.join(Role, Usuario.id_rol == Role.id_rol).filter(Role.nombre_rol == super_role_name).all()
        if not users:
            print(f'No se encontraron usuarios con campo `rol` = "{super_role_name}"')
            return

        updated = 0
        for u in users:
            if u.id_rol != role.id_rol:
                u.id_rol = role.id_rol
                updated += 1
        db.session.commit()
        print(f'Asociado rol {super_role_name} a {updated} usuario(s).')
