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

        # Catálogo técnico único. Los roles solo agrupan estos permisos.
        permisos_base = [
            ('ver_usuarios', 'Consultar usuarios'),
            ('reportes_usuarios', 'Generar reportes de usuarios'),
            ('registrar_usuarios', 'Registrar usuarios'),
            ('editar_usuarios', 'Editar usuarios'),
            ('eliminar_usuarios', 'Eliminar usuarios'),
            ('ver_roles', 'Consultar roles'),
            ('registrar_roles', 'Registrar roles'),
            ('editar_roles', 'Editar roles'),
            ('eliminar_roles', 'Eliminar roles'),
            ('asignar_permisos_roles', 'Asignar permisos a roles'),
            ('ver_permisos', 'Consultar catálogo de permisos'),
            ('registrar_permisos', 'Registrar permisos'),
            ('editar_permisos', 'Editar permisos'),
            ('eliminar_permisos', 'Eliminar permisos'),
            ('ver_bitacora', 'Consultar bitácora'),
            ('ver_catalogos', 'Consultar tablas maestras'),
            ('ver_actividades', 'Consultar actividades'),
            ('registrar_actividades', 'Registrar actividades'),
            ('editar_actividades', 'Editar actividades'),
            ('eliminar_actividades', 'Eliminar actividades'),
            ('cambiar_estado_actividades', 'Cambiar estado de actividades'),
            ('ver_formaciones', 'Consultar formaciones'),
            ('registrar_formaciones', 'Registrar formaciones'),
            ('editar_formaciones', 'Editar formaciones'),
            ('eliminar_formaciones', 'Eliminar formaciones'),
            ('cambiar_estado_formaciones', 'Cambiar estado de formaciones'),
            ('ver_sensibilizaciones', 'Consultar sensibilizaciones'),
            ('registrar_sensibilizaciones', 'Registrar sensibilizaciones'),
            ('editar_sensibilizaciones', 'Editar sensibilizaciones'),
            ('eliminar_sensibilizaciones', 'Eliminar sensibilizaciones'),
            ('cambiar_estado_sensibilizaciones', 'Cambiar estado de sensibilizaciones'),
            ('ver_divulgaciones', 'Consultar divulgaciones'),
            ('reportes_divulgaciones', 'Generar reportes de divulgación'),
            ('registrar_divulgaciones', 'Registrar divulgaciones'),
            ('editar_divulgaciones', 'Editar divulgaciones'),
            ('eliminar_divulgaciones', 'Eliminar divulgaciones'),
            ('aprobar_divulgaciones', 'Aprobar divulgaciones'),
            ('publicar_divulgaciones', 'Publicar divulgaciones'),
            ('despublicar_divulgaciones', 'Retirar divulgaciones publicadas'),
            ('ver_instituciones', 'Consultar instituciones'),
            ('registrar_instituciones', 'Registrar instituciones'),
            ('editar_instituciones', 'Editar instituciones'),
            ('eliminar_instituciones', 'Eliminar instituciones'),
            ('ver_comunidades', 'Consultar comunidades'),
            ('registrar_comunidades', 'Registrar comunidades'),
            ('editar_comunidades', 'Editar comunidades'),
            ('eliminar_comunidades', 'Eliminar comunidades'),
            ('ver_niveles', 'Consultar niveles'),
            ('registrar_niveles', 'Registrar niveles'),
            ('editar_niveles', 'Editar niveles'),
            ('eliminar_niveles', 'Eliminar niveles'),
            ('ver_mapas_riesgo', 'Consultar mapas de riesgo'),
            ('reportes_mapas_riesgo', 'Generar reportes de mapas de riesgo'),
            ('registrar_mapas_riesgo', 'Registrar mapas de riesgo'),
            ('editar_mapas_riesgo', 'Editar mapas de riesgo'),
            ('eliminar_mapas_riesgo', 'Eliminar mapas de riesgo'),
            ('ver_elementos_mapa', 'Consultar elementos de mapas'),
            ('registrar_elementos_mapa', 'Registrar elementos de mapas'),
            ('editar_elementos_mapa', 'Editar elementos de mapas'),
            ('eliminar_elementos_mapa', 'Eliminar elementos de mapas'),
            ('ver_simbologia', 'Consultar simbología'),
            ('registrar_simbologia', 'Registrar simbología'),
            ('editar_simbologia', 'Editar simbología'),
            ('eliminar_simbologia', 'Eliminar simbología'),
            ('ver_mapas_climaticos', 'Consultar mapas climáticos'),
            ('reportes_mapas_climaticos', 'Generar reportes de mapas climáticos'),
            ('registrar_mapas_climaticos', 'Registrar mapas climáticos'),
            ('editar_mapas_climaticos', 'Editar mapas climáticos'),
            ('eliminar_mapas_climaticos', 'Eliminar mapas climáticos'),
            ('ver_inventario', 'Consultar inventario'),
            ('registrar_inventario', 'Registrar equipos de inventario'),
            ('editar_inventario', 'Editar equipos de inventario'),
            ('eliminar_inventario', 'Eliminar equipos de inventario'),
            ('ver_movimientos_inventario', 'Consultar movimientos de inventario'),
            ('registrar_movimientos_inventario', 'Registrar movimientos de inventario'),
            ('editar_movimientos_inventario', 'Editar movimientos de inventario'),
            ('eliminar_movimientos_inventario', 'Eliminar movimientos de inventario'),
            ('ver_reportes_inventario', 'Generar reportes de inventario'),
            ('ver_actas_inventario', 'Consultar actas de responsabilidad'),
            ('ver_tecnicos', 'Consultar técnicos de campo'),
            ('editar_mi_tecnico', 'Editar los datos propios del técnico'),
            ('registrar_tecnicos', 'Registrar técnicos de campo'),
            ('editar_tecnicos', 'Editar técnicos de campo'),
            ('eliminar_tecnicos', 'Eliminar técnicos de campo'),
            ('ver_movimientos_tecnicos', 'Consultar movimientos de técnicos'),
            ('ver_reportes_tecnicos', 'Generar reportes de técnicos'),
            ('reportes_roles', 'Generar reportes de roles'),
            ('reportes_permisos', 'Generar reportes de permisos'),
            ('reportes_formaciones', 'Generar reportes de formaciones'),
            ('reportes_sensibilizaciones', 'Generar reportes de sensibilizaciones'),
            ('reportes_actividades', 'Generar reportes de actividades'),
            ('consultar_geografia', 'Consultar catálogos geográficos'),
            # Compatibilidad con instalaciones anteriores.
            ('gestionar_usuarios', 'Compatibilidad: administrar seguridad'),
            ('gestionar_monitoreo', 'Compatibilidad: administrar monitoreo'),
            ('gestionar_actividades', 'Compatibilidad: administrar actividades'),
            ('gestionar_formaciones', 'Compatibilidad: administrar formaciones'),
            ('gestionar_sensibilizaciones', 'Compatibilidad: administrar sensibilizaciones'),
            ('crear_divulgaciones', 'Compatibilidad: crear divulgaciones'),
            ('aprobar_divulgaciones', 'Compatibilidad: aprobar divulgaciones'),
            ('gestionar_geomatica', 'Compatibilidad: administrar geomática'),
            ('ver_mapas', 'Compatibilidad: consultar mapas'),
            ('gestionar_inventario', 'Compatibilidad: administrar inventario'),
            ('gestionar_tecnicos', 'Compatibilidad: administrar técnicos'),
        ]

        permisos_creados = {}
        ultimo_permiso = Permission.query.order_by(Permission.id_modulo.desc()).first()
        siguiente_id_permiso = (ultimo_permiso.id_modulo + 1) if ultimo_permiso else 1
        for nombre_permiso, descripcion_permiso in permisos_base:
            permiso = Permission.query.filter_by(nombre=nombre_permiso).first()
            if not permiso:
                permiso = Permission(
                    id_modulo=siguiente_id_permiso,
                    nombre=nombre_permiso,
                    descripcion=descripcion_permiso,
                )
                siguiente_id_permiso += 1
                db.session.add(permiso)
            permisos_creados[nombre_permiso] = permiso

        db.session.commit()

        # Administrador conserva la separación operativa: no aprueba publicaciones.
        admin_permisos = [nombre for nombre, _ in permisos_base
                          if nombre not in ('aprobar_divulgaciones', 'publicar_divulgaciones', 'despublicar_divulgaciones')]
        for permiso_nombre in admin_permisos:
            permiso = permisos_creados[permiso_nombre]
            if permiso not in admin_role.permissions:
                admin_role.permissions.append(permiso)

        for permiso_nombre, _ in permisos_base:
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
