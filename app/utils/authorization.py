from functools import wraps
from flask import abort, redirect, url_for, flash, current_app
from flask_login import current_user


SUPERUSER_ROLE_IDS = (1, 2)
PERMISSION_ALIASES = {
    'manage_users': 'gestionar_usuarios',
    'manage_roles': 'gestionar_usuarios',
}

PERMISSION_FALLBACKS = {
    'ver_usuarios': ('gestionar_usuarios',),
    'registrar_usuarios': ('gestionar_usuarios',),
    'editar_usuarios': ('gestionar_usuarios',),
    'eliminar_usuarios': ('gestionar_usuarios',),
    'ver_roles': ('gestionar_usuarios',),
    'registrar_roles': ('gestionar_usuarios',),
    'editar_roles': ('gestionar_usuarios',),
    'eliminar_roles': ('gestionar_usuarios',),
    'asignar_permisos_roles': ('gestionar_usuarios',),
    'ver_permisos': ('gestionar_usuarios',),
    'registrar_permisos': ('gestionar_usuarios',),
    'editar_permisos': ('gestionar_usuarios',),
    'eliminar_permisos': ('gestionar_usuarios',),
    'ver_bitacora': ('gestionar_usuarios',),
    'ver_actividades': ('gestionar_actividades', 'gestionar_monitoreo'),
    'registrar_actividades': ('gestionar_actividades', 'gestionar_monitoreo'),
    'editar_actividades': ('gestionar_actividades', 'gestionar_monitoreo'),
    'eliminar_actividades': ('gestionar_actividades', 'gestionar_monitoreo'),
    'cambiar_estado_actividades': ('gestionar_actividades', 'gestionar_monitoreo'),
    'ver_formaciones': ('gestionar_formaciones',),
    'registrar_formaciones': ('gestionar_formaciones',),
    'editar_formaciones': ('gestionar_formaciones',),
    'eliminar_formaciones': ('gestionar_formaciones',),
    'cambiar_estado_formaciones': ('gestionar_formaciones',),
    'ver_sensibilizaciones': ('gestionar_sensibilizaciones',),
    'registrar_sensibilizaciones': ('gestionar_sensibilizaciones',),
    'editar_sensibilizaciones': ('gestionar_sensibilizaciones',),
    'eliminar_sensibilizaciones': ('gestionar_sensibilizaciones',),
    'cambiar_estado_sensibilizaciones': ('gestionar_sensibilizaciones',),
    'ver_divulgaciones': ('crear_divulgaciones', 'aprobar_divulgaciones'),
    'registrar_divulgaciones': ('crear_divulgaciones',),
    'editar_divulgaciones': ('crear_divulgaciones',),
    'eliminar_divulgaciones': ('crear_divulgaciones',),
    'ver_mapas_riesgo': ('gestionar_geomatica', 'ver_mapas'),
    'registrar_mapas_riesgo': ('gestionar_geomatica',),
    'editar_mapas_riesgo': ('gestionar_geomatica',),
    'eliminar_mapas_riesgo': ('gestionar_geomatica',),
    'ver_elementos_mapa': ('gestionar_geomatica',),
    'registrar_elementos_mapa': ('gestionar_geomatica',),
    'editar_elementos_mapa': ('gestionar_geomatica',),
    'eliminar_elementos_mapa': ('gestionar_geomatica',),
    'ver_simbologia': ('gestionar_geomatica',),
    'registrar_simbologia': ('gestionar_geomatica',),
    'editar_simbologia': ('gestionar_geomatica',),
    'eliminar_simbologia': ('gestionar_geomatica',),
    'ver_mapas_climaticos': ('gestionar_geomatica', 'ver_mapas'),
    'registrar_mapas_climaticos': ('gestionar_geomatica',),
    'editar_mapas_climaticos': ('gestionar_geomatica',),
    'eliminar_mapas_climaticos': ('gestionar_geomatica',),
    'ver_inventario': ('gestionar_inventario',),
    'registrar_inventario': ('gestionar_inventario',),
    'editar_inventario': ('gestionar_inventario',),
    'eliminar_inventario': ('gestionar_inventario',),
    'ver_movimientos_inventario': ('gestionar_inventario',),
    'registrar_movimientos_inventario': ('gestionar_inventario',),
    'editar_movimientos_inventario': ('gestionar_inventario',),
    'eliminar_movimientos_inventario': ('gestionar_inventario',),
    'ver_reportes_inventario': ('gestionar_inventario',),
    'ver_actas_inventario': ('gestionar_inventario',),
    'ver_tecnicos': ('gestionar_tecnicos',),
    'registrar_tecnicos': ('gestionar_tecnicos',),
    'editar_tecnicos': ('gestionar_tecnicos',),
    'eliminar_tecnicos': ('gestionar_tecnicos',),
    'ver_movimientos_tecnicos': ('gestionar_tecnicos',),
    'ver_reportes_tecnicos': ('gestionar_tecnicos',),
    'consultar_geografia': (),
    'ver_catalogos': ('ver_instituciones', 'ver_comunidades', 'ver_niveles', 'gestionar_usuarios'),
    'ver_instituciones': ('gestionar_usuarios',),
    'registrar_instituciones': ('gestionar_usuarios',),
    'editar_instituciones': ('gestionar_usuarios',),
    'eliminar_instituciones': ('gestionar_usuarios',),
    'ver_comunidades': ('gestionar_usuarios',),
    'registrar_comunidades': ('gestionar_usuarios',),
    'editar_comunidades': ('gestionar_usuarios',),
    'eliminar_comunidades': ('gestionar_usuarios',),
    'ver_niveles': ('gestionar_usuarios',),
    'registrar_niveles': ('gestionar_usuarios',),
    'editar_niveles': ('gestionar_usuarios',),
    'eliminar_niveles': ('gestionar_usuarios',),
}


def _normalize_permission_name(permission_name):
    if not permission_name:
        return ''
    return PERMISSION_ALIASES.get(permission_name, permission_name)


def current_role_id(default=None):
    try:
        return int(getattr(current_user, 'id_rol', default))
    except (TypeError, ValueError):
        return default


def is_superuser():
    return current_role_id() in SUPERUSER_ROLE_IDS


def current_permission_names():
    if not current_user.is_authenticated:
        return []

    try:
        permisos = []
        for name in getattr(current_user, 'permission_names', []):
            if name:
                permisos.append(name)
                alias = PERMISSION_ALIASES.get(name)
                if alias:
                    permisos.append(alias)
        return list(dict.fromkeys(permisos))
    except Exception:
        return []


def has_permission(permission_name):
    if not current_user.is_authenticated:
        return False

    if is_superuser():
        return True

    permission_name = _normalize_permission_name(permission_name)

    try:
        candidates = (permission_name,) + PERMISSION_FALLBACKS.get(permission_name, ())
        return current_user.has_permission(*candidates)
    except Exception:
        permissions = set(current_permission_names())
        candidates = (permission_name,) + PERMISSION_FALLBACKS.get(permission_name, ())
        return any(candidate in permissions for candidate in candidates)


def verificar_permiso_dinamico(permission_name):
    """Reject unauthorised requests while keeping superuser bypass centralised."""
    if not current_user.is_authenticated:
        abort(403)

    if is_superuser():
        return True

    if not has_permission(permission_name):
        flash('No tiene privilegios institucionales para acceder a este módulo.', 'error')
        abort(403)

    return True


def role_required(*role_names):
    """Decorator: permite acceso solo si el usuario tiene alguno de los roles listados."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debe iniciar sesión para acceder a esta sección.', 'error')
                return redirect(url_for('auth.login'))

            # Si el usuario tiene el rol superusuario configurado, permitir siempre
            try:
                super_role = (current_app.config.get('SUPER_ROLE_NAME') or '').strip().lower()
                user_role_field = (getattr(current_user, 'rol', '') or '').strip().lower()
                if super_role and (user_role_field == super_role or current_user.has_role(super_role)):
                    return f(*args, **kwargs)
            except Exception:
                pass

            # Permitir si tiene alguno de los roles (revisar relación many-to-many).
            for rn in role_names:
                if current_user.has_role(rn):
                    return f(*args, **kwargs)

            # Sin permiso: redirigir sin flash (para evitar mensajes confusos).
            return redirect(url_for('dashboard'))

        return wrapped
    return decorator


def permission_required(*permission_names):
    """Decorator: permite acceso si el usuario tiene alguno de los permisos listados."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debe iniciar sesión para acceder a esta sección.', 'error')
                return redirect(url_for('auth.login'))

            # Si el usuario tiene el rol superusuario configurado, permitir siempre
            try:
                super_role = (current_app.config.get('SUPER_ROLE_NAME') or '').strip().lower()
                user_role_field = (getattr(current_user, 'rol', '') or '').strip().lower()
                if super_role and (user_role_field == super_role or current_user.has_role(super_role)):
                    return f(*args, **kwargs)
            except Exception:
                pass

            for pn in permission_names:
                if has_permission(pn):
                    return f(*args, **kwargs)

            flash('No tiene permisos suficientes para acceder a esta sección.', 'error')
            return redirect(url_for('dashboard'))

        return wrapped
    return decorator
